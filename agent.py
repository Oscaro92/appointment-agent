# * import libraries
import os, json, uuid
from decouple import config
from typing import Optional
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import JSONLoader

# * import functions
from function import getBusy, createRDV


class AppointmentInfo(BaseModel):
    summary: Optional[str] = Field(default=None, description="Nom du rendez-vous")
    full_name: Optional[str] = Field(default=None, description="Nom complet du client")
    date_start: Optional[str] = Field(default=None, description="Date de début du rendez-vous format ISO 8601 UTC de la france")
    date_end: Optional[str] = Field(default=None, description="Date de fin du rendez-vous au format ISO 8601 UTC de la france")
    phone: Optional[str] = Field(default=None, description="Numéro de téléphone")
    email: Optional[str] = Field(default=None, description="Adresse email")
    action_needed: str = Field(description="Action à effectuer: 'continue', 'get_rdv', 'create_rdv'")
    content: str = Field(description="Response attendu coté client/humain")


class AgentRDV():
    def __init__(self):
        temperature = 0.5
        model = "gpt-4o-mini"
        os.environ["OPENAI_API_KEY"] = config('OPENAI_API_KEY')

        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.rdv = []
        self.isTaken = False

    def loadDoc(self) -> list:
        '''
        Load all documents (RAG)

        :return: list of json (Appointment)
        '''

        appointments = getBusy()

        tempo_uuid = uuid.uuid4()

        with open(f'{tempo_uuid}.json', 'w', encoding='utf-8') as f:
            json.dump(
                appointments,
                f,
                default=str
            )

        loader = JSONLoader(
            file_path=f"{tempo_uuid}.json",
            jq_schema=".",
            text_content=False
        )

        docs = loader.load()

        os.remove(f"{tempo_uuid}.json")

        return docs


    def process_action(self, appointment_info: AppointmentInfo) -> None:
        """Traite les actions nécessaires selon l'état de la conversation"""
        if appointment_info['action_needed'] == "get_rdv":
            self.rdv = getBusy()
        elif appointment_info['action_needed'] == "create_rdv" and not self.isTaken:
            createRDV(appointment_info)



    def chat(self, query: list) -> str:
        '''
        get response of LLM

        :param docs: list of docs similary
        :param query: user request
        :return: LLM response
        '''

        try:
            parser = JsonOutputParser(pydantic_object=AppointmentInfo)
            parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

            date_now = datetime.now()
            date_format = date_now.strftime("%A %d %B %Y")

            template = [
                (
                    "system",
                    f"""
                    Vous êtes une assistante écrit française pour Pigalle Immobilier, un cabinet de conseil en immobilier situé au 123 Avenue des Champs-Élysées, Paris. Votre rôle est d'aider en français les clients à planifier des rendez-vous avec Oscar Moisset.

                    CONTEXTE IMPORTANT:
                    Voici la liste des rendez-vous déjà programmés: {self.rdv}
                    Vous devez ABSOLUMENT vérifier cette liste avant de proposer des créneaux et NE JAMAIS proposer un créneau qui chevauche un rendez-vous existant.
                    Les rendez-vous durent 15 ou 30 mins.
                    Heures disponibles: 9h-18h du lundi au vendredi uniquement.
                    Aujourd'hui nous sommes le {date_format}.

                    FORMAT DE RÉPONSE REQUIS:
                    Vous devez retourner un JSON structuré avec:
                    - summary: nom du client et de l'hôte
                    - full_name: nom et prénom du client
                    - date_start: début du RDV (ISO 8601 UTC de la Europe/Paris)
                    - date_end: fin du RDV (ISO 8601 UTC de la Europe/Paris)
                    - phone: téléphone du client
                    - email: email du client
                    - action_needed: 
                        * 'continue' (défaut)
                        * 'get_rdv' (vérifier les disponibilités)
                        * 'create_rdv' (créer le RDV)
                    - content: votre réponse au client

                    PROCESSUS DE PRISE DE RENDEZ-VOUS:
                    1. Demander le nom complet du client, toujours vouvoyer le client et utiliser son prénom pour s'adresser à lui
                    2. Pour la date/heure:
                       - Demander leurs préférences
                       - action_needed = 'get_rdv' quand vous vérifiez les disponibilités
                       - Vérifier les conflits avec {self.rdv}
                       - Si conflit: proposer 2 autres créneaux proches
                    3. Une fois le créneau choisi:
                       - Demander téléphone et email
                       - Confirmer tous les détails et les listant dans content :
                         * Nom complet du client
                         * Date du rendez-vous
                         * Le numéro de téléphone et email du client
                    4. Une fois le informations confirmé par le client:
                       - action_needed = 'create_rdv' pour finaliser

                    RÈGLES DE GESTION DES CONFLITS:
                    - Si un créneau demandé existe dans {self.rdv}, proposer 2 alternatives:
                      * Le créneau disponible le plus proche avant
                      * Le créneau disponible le plus proche après
                    - Tenir compte des horaires d'ouverture (9h-18h)
                    - Pas de rendez-vous les weekends
                    """
                )
            ]
            for q in query:
                template.append((q["role"], q["content"]))

            prompt = ChatPromptTemplate.from_messages(template)

            chain = prompt | self.llm | parser

            response = chain.invoke({})

            print(response)

            self.process_action(response)
            return response['content']
        except Exception as e:
            print(f"Error {e}")
            return "Désolé, une erreur est survenue lors du traitement de votre demande."
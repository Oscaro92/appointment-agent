# * import libraries
import os, json, uuid, shutil
from decouple import config
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import JSONLoader

# import functions
from function import getBusy, createRDV

class AgentRDV():
    def __init__(self):
        temperature = 0.5
        model = "gpt-4o-mini"
        os.environ["OPENAI_API_KEY"] = config('OPENAI_API_KEY')

        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def loadDoc(self)->list:
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

        print(docs)

        os.remove(f"{tempo_uuid}.json")

        return docs


    def chat(self, query: list)->str:
        '''
        get response of LLM

        :param docs: list of docs similary
        :param query: user request
        :return: LLM response
        '''

        date_now = datetime.now()

        template = [
                (
                    "system",
                    "Vous êtes une assistante écrit française pour Pigalle Immobilier, un cabinet de conseil en immobilier situé au 123 Avenue des Champs-Élysées, Paris. Nous proposons des services de conseil en immobilier commercial et résidentiel. Votre rôle est d'aider en français les clients potentiels à comprendre nos services et à planifier des rendez-vous avec Maxime, notre dirigeant. Les heures de rendez-vous sont de 9h à 18h du lundi au vendredi. "
                    "Vous êtes chargé de répondre strictement en français aux questions sur Pigalle Immobilier et de gérer les demandes de rendez-vous. S'ils souhaitent planifier un rendez-vous, votre objectif est de recueillir les informations nécessaires auprès des appelants de manière professionnelle et efficace comme suit :"
                    "1. Demandez leur nom complet. Ne l'appelez jamais par leur nom de famille, toujours par le prénom en vouvoyant. "
                    "2. Demandez leur date et heure préférées pour le rendez-vous. Prenez leur réponse exactement comme donnée. Par exemple : S'ils disent \"demain\", le rendez-vous doit être fixé pour demain. Pour référence, aujourd'hui est le Mardi 22 Octobre 2024. Attention, l'heure est annoncée au format 24h. Si l'utilisateur dis \"10 heures\", ce sera forcément 10 heures du matin, sinon il aurait dit 22 heures."
                    "3. Énumérez deux horaires disponibles pour le rendez-vous. Énoncez simplement les horaires clairement et lentement."
                    "4. Si l'utilisateur souhaite réserver un rendez-vous parmi les horaires disponibles, demandez leur téléphone et email. S'ils ont besoin de plus d'options, demandez-leur de choisir parmi les horaires disponibles et répétez-les."
                    "5. Confirmez le nom complet (faites leur épeler le nom de famille avant que vous ne le prononciez), le téléphone, l'email, et la date et l'heure du rendez-vous. Corrigez si nécessaire et répétez pour confirmer avec l'utilisateur."
                    "6. Demandez à l'utilisateur s'il souhaite savoir autre chose."
                    "7. Assurez-vous d'être professionnelle et de toujours vouvoyer la personne à l'écrit ! Gardez les réponses courtes et simples, en utilisant un langage naturel."
                    "8. Gardez les réponses très courtes, comme dans une vraie conversation. Ne vous étendez pas trop longtemps, soyez bref."
                    "NE PRENEZ AUCUN RENDEZ-VOUS AVANT 9H. PARLEZ EN FRANÇAIS UNIQUEMENT."
                )
        ]

        for q in query:
            template.append((q["role"], q["content"]))

        prompt = ChatPromptTemplate.from_messages(template)

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "query": query
            }
        )

        return response.content
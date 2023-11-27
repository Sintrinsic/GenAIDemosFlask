import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from openai import OpenAI


class OpenAIClient:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            # Fetch API key from config file
            api_key = cls.get_secret()
            cls._instance = cls(api_key)
        return cls._instance

    def __init__(self, api_key=None):
        if self._instance is not None:
            raise Exception("This class is a singleton. Call GlobalEventFilter.getInstance() instead.")
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def call_whisper_api(self, audio_file_path):
        # Use OpenAI Python package method for Whisper
        audio_file = open(audio_file_path, "rb")
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        response = transcript
        return response

    def call_tts_api(self, text, voice, speed, filename="temp_audio.mp3"):
        temp_file_path = f"recordings/{filename}"
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,  # was nova
            input=text,
            speed=speed
        )
        response.stream_to_file(temp_file_path)
        return temp_file_path

    def call_chat_completion(self, model, message_list):
        response = self.client.chat.completions.create(
            model=model,
            messages=message_list
        )
        assistant_message = response.choices[0].message.content
        return assistant_message

    # Use this code snippet in your app.
    # If you need more information about configurations
    # or implementing the sample code, visit the AWS docs:
    # https://aws.amazon.com/developer/language/python/

    @staticmethod
    def get_secret():

        secret_name = "openapi_secret"
        region_name = "us-west-2"

        # Create a Secrets Manager client
        try:
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )

            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            api_key = get_secret_value_response['SecretString']
        except (ClientError, NoCredentialsError) as e:
            print(f"Error in fetching AWS secret: {e}")
            print("Attempting to load secret key from local file.")
            with open("secret_key.txt") as f:
                api_key = f.readline()
            print(f"AWS secrets not available. Using local secret key.")

        return api_key

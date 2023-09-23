from src.common import config, artificer

class Response:
    @classmethod
    def load(cls) -> dict:
        return config.Constants.response

    def __init__(self, response_type: str, response: str):
        if not response.endswith('\n'):
            response += '\n'
        self.raw = response
        self.__resp = self.load()
        artist = artificer.Artificer(self.__resp[response_type], self.raw)
        self.art = artist.touch()

    def to_string(self) -> str:
        return f"```ansi\n{self.art}```"

    def __add__(self, other_response):
        if isinstance(other_response, Response):
            return Response(self.raw + other_response.art)
        elif isinstance(other_response, str):
            return Response(self.raw + other_response)
        else:
            raise TypeError('Unsupported operand for +')
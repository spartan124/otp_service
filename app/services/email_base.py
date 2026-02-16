from abc import ABC, abstractmethod

class EmailProvider(ABC):
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Sends an email. Returns True if successful, False otherwise.
        Must be implemented by all subclasses.
        """
        pass
    
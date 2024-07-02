from django.test import Client
from ..host_api import router


class HostClient:

    def delete_client(self):
        self.user.delete()

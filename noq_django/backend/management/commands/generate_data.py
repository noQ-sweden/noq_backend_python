from django.core.management.base import BaseCommand
from backend.scripts import generate_data  # ← make sure your script has a run() function

class Command(BaseCommand):
    help = 'Generate mock data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating mock data...")
        generate_data.run()
        self.stdout.write("✅ Mock data generation complete.")
from django.apps import AppConfig

class TransactionsConfig(AppConfig):
    name = 'transactions'

    def ready(self):
        import transactions.signals  # Ensure this import is present

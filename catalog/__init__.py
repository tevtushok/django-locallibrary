from django.db.backends.signals import connection_created
def activate_case_sensitive_like(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA case_sensitive_like=ON;')

#connection_created.connect(activate_case_sensitive_like)

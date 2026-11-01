from django.db import migrations

SERVICES = [
    ('Женская стрижка', 'Мытьё, стрижка, укладка', 'от 800 сом'),
    ('Мужская стрижка', 'Классическая или модельная', 'от 500 сом'),
    ('Окрашивание', 'Однотонное, мелирование, сложные техники', 'от 2000 сом'),
    ('Маникюр', 'С покрытием или без', 'от 700 сом'),
    ('Укладка', 'Повседневная и вечерняя', 'от 600 сом'),
]


def seed(apps, schema_editor):
    Service = apps.get_model('salon', 'Service')
    if not Service.objects.exists():
        for i, (name, desc, price) in enumerate(SERVICES):
            Service.objects.create(name=name, description=desc, price=price, order=i)


class Migration(migrations.Migration):
    dependencies = [('salon', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]

# Generated migration for StudentAssignment model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0001_initial'),
        ('students', '0001_initial'),
        ('praktikums_lehrkraft', '0001_initial'),
        ('schools', '0001_initial'),
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignment_status', models.CharField(choices=[('ASSIGNED', 'Assigned'), ('CONFIRMED', 'Confirmed'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='ASSIGNED', max_length=20)),
                ('assignment_date', models.DateField(auto_now_add=True)),
                ('academic_year', models.CharField(default='2025/26', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='praktikums_lehrkraft.praktikumslehrkraft')),
                ('practicum_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='subjects.praktikumtype')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='schools.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='praktikum_assignments', to='students.student')),
                ('subject', models.ForeignKey(blank=True, help_text='Subject for this practicum (required for SFP/ZSP)', null=True, on_delete=django.db.models.deletion.PROTECT, to='subjects.subject')),
            ],
            options={
                'verbose_name': 'Student Assignment',
                'verbose_name_plural': 'Student Assignments',
                'indexes': [models.Index(fields=['student', 'practicum_type'], name='assignments_student_6e8f5a_idx'), models.Index(fields=['mentor', 'practicum_type'], name='assignments_mentor_i_e20c29_idx'), models.Index(fields=['assignment_status'], name='assignments_assignme_7fcbbd_idx')],
                'unique_together': {('student', 'practicum_type', 'academic_year')},
            },
        ),
    ]

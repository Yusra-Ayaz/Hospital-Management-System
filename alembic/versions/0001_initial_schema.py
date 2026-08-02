"""Initial hospital schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def id_column(): return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True)
def timestamps(columns):
    return columns + [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]
def upgrade():
    op.create_table("users", *timestamps([id_column(),sa.Column("email",sa.String(320),nullable=False),sa.Column("full_name",sa.String(150),nullable=False),sa.Column("password_hash",sa.String(255),nullable=False),sa.Column("role",sa.String(30),nullable=False,server_default="staff"),sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true())])); op.create_index("ix_users_email","users",["email"],unique=True)
    op.create_table("patients", *timestamps([id_column(),sa.Column("medical_record_number",sa.String(30),nullable=False),sa.Column("first_name",sa.String(80),nullable=False),sa.Column("last_name",sa.String(80),nullable=False),sa.Column("date_of_birth",sa.Date(),nullable=False),sa.Column("gender",sa.String(20),nullable=False),sa.Column("phone",sa.String(30),nullable=False),sa.Column("email",sa.String(320)),sa.Column("address",sa.Text()),sa.Column("blood_type",sa.String(5)),sa.Column("emergency_contact",sa.String(150))])); op.create_index("ix_patients_medical_record_number","patients",["medical_record_number"],unique=True)
    op.create_table("doctors", *timestamps([id_column(),sa.Column("first_name",sa.String(80),nullable=False),sa.Column("last_name",sa.String(80),nullable=False),sa.Column("specialization",sa.String(120),nullable=False),sa.Column("license_number",sa.String(60),nullable=False),sa.Column("phone",sa.String(30),nullable=False),sa.Column("email",sa.String(320),nullable=False),sa.Column("room_number",sa.String(20))])); op.create_index("ix_doctors_specialization","doctors",["specialization"]); op.create_index("ix_doctors_license_number","doctors",["license_number"],unique=True); op.create_index("ix_doctors_email","doctors",["email"],unique=True)
    op.create_table("appointments", *timestamps([id_column(),sa.Column("patient_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("patients.id",ondelete="CASCADE"),nullable=False),sa.Column("doctor_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("doctors.id"),nullable=False),sa.Column("scheduled_at",sa.DateTime(timezone=True),nullable=False),sa.Column("reason",sa.Text(),nullable=False),sa.Column("status",sa.String(20),nullable=False,server_default="scheduled"),sa.Column("notes",sa.Text())])); op.create_index("ix_appointments_patient_id","appointments",["patient_id"]);op.create_index("ix_appointments_doctor_id","appointments",["doctor_id"]);op.create_index("ix_appointments_scheduled_at","appointments",["scheduled_at"])
    op.create_table("medical_records", *timestamps([id_column(),sa.Column("patient_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("patients.id",ondelete="CASCADE"),nullable=False),sa.Column("doctor_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("doctors.id")),sa.Column("visit_date",sa.Date(),nullable=False),sa.Column("diagnosis",sa.Text(),nullable=False),sa.Column("treatment",sa.Text()),sa.Column("prescription",sa.Text()),sa.Column("allergies",sa.Text())])); op.create_index("ix_medical_records_patient_id","medical_records",["patient_id"])
def downgrade():
    op.drop_table("medical_records"); op.drop_table("appointments"); op.drop_table("doctors"); op.drop_table("patients"); op.drop_table("users")

from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User


def generate_employee_id(db: Session) -> str:
    """
    Generate a new employee ID like AW001, AW002, ...
    Uses last user's id to compute next number.
    """
    last_user = db.query(User).order_by(User.id.desc()).first()
    next_number = (last_user.id if last_user else 0) + 1
    return f"AW{str(next_number).zfill(3)}"


def seed_initial_data(db: Session):
    # Seed roles if empty
    if db.query(Role).count() == 0:
        default_roles = [
            ("admin", "Full access"),
            ("employee", "Standard employee"),
            ("hr", "HR staff"),
            ("manager", "Team manager"),
        ]
        for name, desc in default_roles:
            db.add(Role(name=name, description=desc))
        db.commit()

    # Seed one Super Admin if no users
    if db.query(User).count() == 0:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            admin = User(
                emp_id=generate_employee_id(db),  # e.g. AW001
                username="admin",                 # NEW required field
                full_name="Super Admin",
                email="admin@example.com",
                dept="Admin",                     # optional, can be None
                is_active=True,
                role=admin_role,
            )
            admin.set_password("admin123")        # default password
            db.add(admin)
            db.commit()

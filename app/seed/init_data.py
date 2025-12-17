from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.models.department import Department


def generate_employee_id(db: Session) -> str:
    last_user = db.query(User).order_by(User.id.desc()).first()
    next_number = (last_user.id if last_user else 0) + 1
    return f"AW{str(next_number).zfill(3)}"


def seed_initial_data(db: Session):

    # ==========================
    # SEED ROLES
    # ==========================
    if db.query(Role).count() == 0:
        roles = [
            ("admin", "Full access"),
            ("manager", "Team manager"),
            ("hr", "HR staff"),
            ("employee", "Standard employee"),
        ]
        for name, desc in roles:
            db.add(Role(name=name, description=desc))
        db.commit()

    admin_role = db.query(Role).filter(Role.name == "admin").first()

    # ==========================
    # SEED DEPARTMENTS
    # ==========================
    if db.query(Department).count() == 0:
        departments = [
            "Admin",
            "Manager",
            "HR",
            "Web Development",
            "Graphic Design",
            "UI / UX",
            "Video",
            "Intern",
            "Content Writing",
            "SEO & Social Media",
        ]

        for dept in departments:
            db.add(Department(name=dept, is_active=True))

        db.commit()

    # Get Admin department safely
    admin_department = (
        db.query(Department)
        .filter(Department.name == "Admin")
        .first()
    )

    # ==========================
    # SEED SUPER ADMIN USER
    # ==========================
    if db.query(User).count() == 0 and admin_role and admin_department:
        admin = User(
            emp_id=generate_employee_id(db),
            username="admin",
            full_name="Super Admin",
            email="admin@ayatiworks.com",
            role=admin_role,
            department=admin_department,  # ✅ SAFE FK
            is_active=True,
        )
        admin.set_password("admin123")
        db.add(admin)
        db.commit()

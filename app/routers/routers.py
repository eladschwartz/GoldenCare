from . import user, auth, department, patient, treatment, goldencare

ROUTERS = [
    user.router,
    auth.router,
    department.router,
    patient.router,
    treatment.router,
    goldencare.router
]
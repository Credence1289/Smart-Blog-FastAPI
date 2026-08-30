from app.tasks.email_tasks import send_password_reset_email

task = send_password_reset_email.delay(
    "your-email@example.com",
    "test-token"
)

print(task.id)
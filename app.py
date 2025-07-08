from app_factory import create_app
import os


app = create_app()


app.run(
    host="0.0.0.0",
    port=5000,
    debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true"
)


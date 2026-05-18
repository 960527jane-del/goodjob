from app import create_app
from app.models import db
from app.models.pet import Pet
from app.models.feed_inventory import FeedInventory

app = create_app()
with app.app_context():
    try:
        pet = Pet.create(user_id=1, name="我的寶貝")
        print("Pet create:", pet)
    except Exception as e:
        print("Pet error:", repr(e))
        
    try:
        inventory = FeedInventory.create(user_id=1, count=0)
        print("Inventory create:", inventory)
    except Exception as e:
        print("Inventory error:", repr(e))

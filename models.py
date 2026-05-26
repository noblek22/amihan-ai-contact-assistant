class Contact:

    def __init__(
        self,
        username,
        name,
        phone
    ):
        self._username = username
        self._name = None
        self._phone = None

        self.name = name
        self.phone = phone

    # -----------------------------
    # USERNAME
    # -----------------------------
    @property
    def username(self):
        return self._username

    # -----------------------------
    # NAME
    # -----------------------------
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):

        if not value or not value.strip():
            raise ValueError(
                "Name cannot be empty"
            )

        self._name = value.strip()

    # -----------------------------
    # PHONE
    # -----------------------------
    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):

        if not value.isdigit():
            raise ValueError(
                "Phone must contain only digits"
            )

        self._phone = value

    # -----------------------------
    # SERIALIZATION
    # -----------------------------
    def to_dict(self):

        return {
            "username": self.username,
            "name": self.name,
            "phone": self.phone
        }

    @staticmethod
    def from_dict(data):

        return Contact(
            username=data.get(
                "username",
                "unknown"
            ),
            name=data["name"],
            phone=data["phone"]
        )

    # -----------------------------
    # STRING DISPLAY
    # -----------------------------
    def __str__(self):

        return (
            f"{self.username} | "
            f"{self.name} | "
            f"{self.phone}"
        )
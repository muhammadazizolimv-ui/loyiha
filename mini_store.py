# Mini Store — mahsulotlar boshqaruvi (konsol dasturi)
# Imkoniyatlar: qo'shish, ko'rish, qidirish, o'zgartirish, o'chirish, faylda saqlash

import json
import os

FAYL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mahsulotlar.json")


def pul(summa):
    """4500000 -> '4 500 000'"""
    return f"{summa:,}".replace(",", " ")


class Mahsulot:
    def __init__(self, nom, narx, miqdor):
        self.nom = nom
        self.narx = narx
        self.miqdor = miqdor

    def jami_qiymat(self):
        return self.narx * self.miqdor

    def __str__(self):
        return f"{self.nom} — {pul(self.narx)} so'm, {self.miqdor} dona"

    def to_dict(self):
        return {"nom": self.nom, "narx": self.narx, "miqdor": self.miqdor}

    @classmethod
    def from_dict(cls, malumot):
        return cls(malumot["nom"], malumot["narx"], malumot["miqdor"])


class Magazin:
    def __init__(self, fayl=FAYL):
        self.fayl = fayl
        self.mahsulotlar = []
        self.yukla()

    def __len__(self):
        return len(self.mahsulotlar)

    # ---------- Qidirish ----------
    def topish(self, nom):
        """Nomi aynan mos mahsulotni qaytaradi (katta-kichik harfga e'tibor bermaydi)."""
        for m in self.mahsulotlar:
            if m.nom.lower() == nom.lower():
                return m
        return None

    def qidir(self, matn):
        """Nomida matn qatnashgan barcha mahsulotlar."""
        return [m for m in self.mahsulotlar if matn.lower() in m.nom.lower()]

    # ---------- Qo'shish / o'zgartirish / o'chirish ----------
    def qosh(self, nom, narx, miqdor):
        if self.topish(nom):
            return False
        self.mahsulotlar.append(Mahsulot(nom, narx, miqdor))
        self.saqla()
        return True

    def ozgartir(self, nom, yangi_nom=None, narx=None, miqdor=None):
        mahsulot = self.topish(nom)
        if mahsulot is None:
            return "topilmadi"
        if yangi_nom and yangi_nom.lower() != mahsulot.nom.lower():
            if self.topish(yangi_nom):
                return "nom_band"
            mahsulot.nom = yangi_nom
        elif yangi_nom:
            mahsulot.nom = yangi_nom
        if narx is not None:
            mahsulot.narx = narx
        if miqdor is not None:
            mahsulot.miqdor = miqdor
        self.saqla()
        return "ok"

    def ochir(self, nom):
        mahsulot = self.topish(nom)
        if mahsulot is None:
            return False
        self.mahsulotlar.remove(mahsulot)
        self.saqla()
        return True

    # ---------- Hisobot ----------
    def umumiy_qiymat(self):
        return sum(m.jami_qiymat() for m in self.mahsulotlar)

    # ---------- Faylda saqlash ----------
    def saqla(self):
        with open(self.fayl, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.mahsulotlar], f, ensure_ascii=False, indent=2)

    def yukla(self):
        if not os.path.exists(self.fayl):
            return
        try:
            with open(self.fayl, encoding="utf-8") as f:
                self.mahsulotlar = [Mahsulot.from_dict(d) for d in json.load(f)]
        except (json.JSONDecodeError, KeyError):
            print("Diqqat: fayl buzilgan, bo'sh ro'yxatdan boshlanmoqda.")
            self.mahsulotlar = []


# ====================== Menyu (foydalanuvchi bilan ishlash) ======================

def son_kirit(savol, bosh_mumkin=False):
    """Musbat butun son so'raydi. bosh_mumkin=True bo'lsa, Enter -> None."""
    while True:
        matn = input(savol).strip()
        if bosh_mumkin and matn == "":
            return None
        if matn.isdigit() and int(matn) >= 0:
            return int(matn)
        print("Iltimos, 0 yoki undan katta butun son kiriting!")


def jadval(mahsulotlar):
    if not mahsulotlar:
        print("Mahsulotlar yo'q.")
        return
    print(f"\n{'№':<4}{'Nomi':<22}{'Narxi (so`m)':>14}{'Miqdori':>10}")
    print("-" * 50)
    for i, m in enumerate(mahsulotlar, 1):
        print(f"{i:<4}{m.nom:<22}{pul(m.narx):>14}{m.miqdor:>10}")
    print("-" * 50)


def menyu_korsat():
    print("\n===== MINI STORE =====")
    print("1. Mahsulot qo'shish")
    print("2. Barcha mahsulotlarni ko'rish")
    print("3. Mahsulot qidirish")
    print("4. Mahsulotni o'zgartirish")
    print("5. Mahsulotni o'chirish")
    print("0. Chiqish")


def qoshish(magazin):
    nom = input("Mahsulot nomi: ").strip()
    if not nom:
        print("Nom bo'sh bo'lmasligi kerak!")
        return
    narx = son_kirit("Narxi (so'm): ")
    miqdor = son_kirit("Miqdori (dona): ")
    if magazin.qosh(nom, narx, miqdor):
        print(f"'{nom}' qo'shildi.")
    else:
        print(f"'{nom}' allaqachon mavjud! Uni o'zgartirish bo'limidan yangilang.")


def qidirish(magazin):
    matn = input("Qidirilayotgan nom: ").strip()
    if not matn:
        print("Qidiruv matnini kiriting!")
        return
    topilgan = magazin.qidir(matn)
    if topilgan:
        jadval(topilgan)
    else:
        print("Hech narsa topilmadi.")


def ozgartirish(magazin):
    nom = input("O'zgartiriladigan mahsulot nomi: ").strip()
    mahsulot = magazin.topish(nom)
    if mahsulot is None:
        print("Bunday mahsulot topilmadi.")
        return
    print(f"Hozirgi: {mahsulot}")
    print("(O'zgartirmaslik uchun Enter bosing)")
    yangi_nom = input("Yangi nom: ").strip() or None
    narx = son_kirit("Yangi narx: ", bosh_mumkin=True)
    miqdor = son_kirit("Yangi miqdor: ", bosh_mumkin=True)

    natija = magazin.ozgartir(nom, yangi_nom, narx, miqdor)
    if natija == "ok":
        print("Mahsulot yangilandi.")
    elif natija == "nom_band":
        print("Bunday nomli mahsulot allaqachon bor!")
    else:
        print("Bunday mahsulot topilmadi.")


def ochirish(magazin):
    nom = input("O'chiriladigan mahsulot nomi: ").strip()
    mahsulot = magazin.topish(nom)
    if mahsulot is None:
        print("Bunday mahsulot topilmadi.")
        return
    tasdiq = input(f"'{mahsulot.nom}' o'chirilsinmi? (ha/yo'q): ").strip().lower()
    if tasdiq == "ha":
        magazin.ochir(nom)
        print("O'chirildi.")
    else:
        print("Bekor qilindi.")


def main():
    magazin = Magazin()
    while True:
        menyu_korsat()
        tanlov = input("Tanlang: ").strip()

        if tanlov == "1":
            qoshish(magazin)
        elif tanlov == "2":
            jadval(magazin.mahsulotlar)
            if magazin:
                print(f"Jami mahsulot turi: {len(magazin)}")
                print(f"Ombordagi umumiy qiymat: {pul(magazin.umumiy_qiymat())} so'm")
        elif tanlov == "3":
            qidirish(magazin)
        elif tanlov == "4":
            ozgartirish(magazin)
        elif tanlov == "5":
            ochirish(magazin)
        elif tanlov == "0":
            print("Dastur tugadi. Ma'lumotlar saqlandi. Xayr!")
            break
        else:
            print("Noto'g'ri tanlov, 0 dan 5 gacha raqam kiriting.")


if __name__ == "__main__":
    main()

PROVINCE_REGION: dict[str, str] = {
    # North
    "Hà Nội": "north", "Hải Phòng": "north", "Quảng Ninh": "north",
    "Hải Dương": "north", "Hưng Yên": "north", "Thái Bình": "north",
    "Nam Định": "north", "Ninh Bình": "north", "Hà Nam": "north",
    "Bắc Ninh": "north", "Vĩnh Phúc": "north", "Phú Thọ": "north",
    "Thái Nguyên": "north", "Bắc Giang": "north", "Bắc Kạn": "north",
    "Cao Bằng": "north", "Lạng Sơn": "north", "Lào Cai": "north",
    "Yên Bái": "north", "Hà Giang": "north", "Tuyên Quang": "north",
    "Sơn La": "north", "Điện Biên": "north", "Lai Châu": "north",
    "Hòa Bình": "north",
    # Central
    "Thanh Hóa": "central", "Nghệ An": "central", "Hà Tĩnh": "central",
    "Quảng Bình": "central", "Quảng Trị": "central", "Thừa Thiên Huế": "central",
    "Đà Nẵng": "central", "Quảng Nam": "central", "Quảng Ngãi": "central",
    "Bình Định": "central", "Phú Yên": "central", "Khánh Hòa": "central",
    "Ninh Thuận": "central", "Bình Thuận": "central", "Kon Tum": "central",
    "Gia Lai": "central", "Đắk Lắk": "central", "Đắk Nông": "central",
    "Lâm Đồng": "central",
    # South
    "TP. Hồ Chí Minh": "south", "Bình Dương": "south", "Đồng Nai": "south",
    "Bà Rịa-Vũng Tàu": "south", "Long An": "south", "Tiền Giang": "south",
    "Bến Tre": "south", "Trà Vinh": "south", "Vĩnh Long": "south",
    "Đồng Tháp": "south", "An Giang": "south", "Kiên Giang": "south",
    "Cần Thơ": "south", "Hậu Giang": "south", "Sóc Trăng": "south",
    "Bạc Liêu": "south", "Cà Mau": "south", "Tây Ninh": "south",
    "Bình Phước": "south",
}


def get_region(province: str | None) -> str | None:
    if not province:
        return None
    return PROVINCE_REGION.get(province)

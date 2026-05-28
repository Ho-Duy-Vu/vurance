"""
scripts/generate_sample_pdfs.py — Tạo PDF test cho ClaimFlow
============================================================
Tạo 8 file PDF mẫu để test upload và OCR pipeline:
  - 2 CCCD mẫu (rõ + mờ)
  - 2 hóa đơn viện phí (approve + reject)
  - 2 claim thiên tai (flood + storm)
  - 1 hóa đơn nha khoa
  - 1 hợp đồng bảo hiểm

Chạy: python scripts/generate_sample_pdfs.py
Output: sample_data/pdfs/

Cài đặt: pip install reportlab
"""

from pathlib import Path
from datetime import datetime, timedelta
import random

OUTPUT_DIR = Path("sample_data/pdfs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_pdf(filename: str, lines: list, title: str = ""):
    """Tạo PDF đơn giản từ danh sách dòng text."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            str(OUTPUT_DIR / filename),
            pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("title", parent=styles["Normal"],
            fontSize=14, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceAfter=6)
        normal = ParagraphStyle("normal", parent=styles["Normal"],
            fontSize=10, leading=14)
        bold = ParagraphStyle("bold", parent=styles["Normal"],
            fontSize=10, fontName="Helvetica-Bold", leading=14)

        story = []
        if title:
            story.append(Paragraph(title, title_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
            story.append(Spacer(1, 0.3*cm))

        for line in lines:
            if not line:
                story.append(Spacer(1, 0.15*cm))
            elif line.startswith("**") and line.endswith("**"):
                story.append(Paragraph(line[2:-2], bold))
            elif line.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
                story.append(Spacer(1, 0.1*cm))
            else:
                story.append(Paragraph(line, normal))

        doc.build(story)
        print(f"  ✅ {filename}")
        return True

    except ImportError:
        # Fallback: text file
        txt_name = filename.replace(".pdf", ".txt")
        with open(OUTPUT_DIR / txt_name, "w", encoding="utf-8") as f:
            if title:
                f.write(title + "\n" + "="*50 + "\n\n")
            f.write("\n".join(lines))
        print(f"  📝 {txt_name} (txt fallback — install reportlab for PDF)")
        return False


def run():
    print("\n📄 ClaimFlow — Generating sample documents...\n")

    # ── 1. CCCD MẪU — hợp lệ ─────────────────────────────────────────────────
    make_pdf("cccd_nguyen_van_an.pdf", [
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
        "Độc lập - Tự do - Hạnh phúc",
        "---",
        "",
        "**CĂN CƯỚC CÔNG DÂN**",
        "",
        "Số: 001234567890",
        "",
        "Họ và tên: NGUYỄN VĂN AN",
        "Ngày sinh: 15/03/1990",
        "Giới tính: Nam",
        "Quốc tịch: Việt Nam",
        "",
        "Quê quán: Xã Đức Ninh Đông, TP Đồng Hới, Quảng Bình",
        "Nơi thường trú: 45 Trần Hưng Đạo, Phường Hải Thành, TP Đồng Hới, Quảng Bình",
        "",
        "Có giá trị đến: 15/03/2035",
        "",
        "---",
        "Cấp ngày 15/03/2020 tại Cục Cảnh sát QLHC về TTXH",
    ], "CĂN CƯỚC CÔNG DÂN")

    # ── 2. CCCD MẪU — người dùng HCM ─────────────────────────────────────────
    make_pdf("cccd_le_thi_thu.pdf", [
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
        "Độc lập - Tự do - Hạnh phúc",
        "---",
        "",
        "**CĂN CƯỚC CÔNG DÂN**",
        "",
        "Số: 079345678901",
        "",
        "Họ và tên: LÊ THỊ THU",
        "Ngày sinh: 20/06/1995",
        "Giới tính: Nữ",
        "Quốc tịch: Việt Nam",
        "",
        "Quê quán: Quận 1, TP Hồ Chí Minh",
        "Nơi thường trú: 123 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP Hồ Chí Minh",
        "",
        "Có giá trị đến: 20/06/2035",
        "",
        "---",
        "Cấp ngày 20/06/2020 tại Cục Cảnh sát QLHC về TTXH",
    ], "CĂN CƯỚC CÔNG DÂN")

    # ── 3. HÓA ĐƠN VIỆN PHÍ — APPROVE (viêm phổi) ────────────────────────────
    make_pdf("invoice_viem_phoi_approve.pdf", [
        "Địa chỉ: 78 Giải Phóng, Đống Đa, Hà Nội",
        "Điện thoại: 024.3869.3731 | Website: bachmai.gov.vn",
        "---",
        "",
        "**HÓA ĐƠN VIỆN PHÍ**",
        f"Số HĐ: BM-{datetime.now().year}-051523",
        "",
        "Họ tên bệnh nhân: Nguyễn Văn An",
        "Ngày sinh: 15/03/1990 | Giới tính: Nam",
        "Địa chỉ: 45 Trần Hưng Đạo, TP Đồng Hới, Quảng Bình",
        "",
        f"Ngày nhập viện: {(datetime.now() - timedelta(days=15)).strftime('%d/%m/%Y')}",
        f"Ngày xuất viện: {(datetime.now() - timedelta(days=13)).strftime('%d/%m/%Y')}",
        "",
        "**Chẩn đoán: Viêm phổi thùy phải**",
        "Mã ICD-10: J18.1",
        "Bác sĩ điều trị: BS. CKI Trần Minh Tuấn — Khoa Hô hấp",
        "",
        "---",
        "**CHI TIẾT CHI PHÍ ĐIỀU TRỊ:**",
        "",
        "Tiền phòng nằm viện (2 ngày)           800,000 VND",
        "Thuốc kháng sinh (Amoxicillin + Azithro) 650,000 VND",
        "Xét nghiệm máu toàn phần                350,000 VND",
        "X-quang phổi thẳng                       400,000 VND",
        "Khí dung (2 lần)                          200,000 VND",
        "Phí khám bác sĩ                           200,000 VND",
        "",
        "---",
        "**TỔNG CỘNG: 2,600,000 VND**",
        "Hình thức thanh toán: Tiền mặt",
        "",
        f"Hà Nội, ngày {datetime.now().strftime('%d tháng %m năm %Y')}",
        "Kế toán viện phí                    Trưởng khoa Hô hấp",
        "",
        "[Dấu đỏ Bệnh viện Bạch Mai]",
    ], "BỆNH VIỆN BẠCH MAI")

    # ── 4. HÓA ĐƠN — REJECT (thẩm mỹ) ───────────────────────────────────────
    make_pdf("invoice_tham_my_reject.pdf", [
        "Địa chỉ: 12 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội",
        "Điện thoại: 024.1234.5678",
        "---",
        "",
        "**HÓA ĐƠN DỊCH VỤ THẨM MỸ**",
        f"Số: TMV-{datetime.now().year}-0892",
        "",
        "Khách hàng: Phạm Thị Bình",
        "Ngày sinh: 10/08/1995",
        "SĐT: 0912.345.678",
        "",
        f"Ngày dịch vụ: {datetime.now().strftime('%d/%m/%Y')}",
        "",
        "**Dịch vụ: Nâng mũi cấu trúc sụn tự thân**",
        "Bác sĩ thực hiện: BS. CKI Nguyễn Đức Hùng",
        "Phòng mổ số: 3",
        "",
        "---",
        "**CHI TIẾT:**",
        "",
        "Chi phí phẫu thuật chỉnh hình mũi    15,000,000 VND",
        "Gây mê toàn thân                       2,000,000 VND",
        "Thuốc và vật tư sau phẫu thuật         1,000,000 VND",
        "",
        "---",
        "**TỔNG CỘNG: 18,000,000 VND**",
        "Đã thanh toán: 18,000,000 VND",
        "",
        "[Ký tên và đóng dấu]",
    ], "THẨM MỸ VIỆN QUỐC TẾ ABC")

    # ── 5. CLAIM THIÊN TAI — LŨ LỤT (approve) ────────────────────────────────
    make_pdf("disaster_flood_quangbinh_approve.pdf", [
        "UBND TỈNH QUẢNG BÌNH",
        "Số: 234/BC-UBND",
        "---",
        "",
        "**BIÊN BẢN XÁC NHẬN THIỆT HẠI DO THIÊN TAI**",
        "",
        "Kính gửi: Công ty Bảo hiểm ClaimFlow",
        "",
        "UBND xã Đức Ninh Đông, TP Đồng Hới, tỉnh Quảng Bình xác nhận:",
        "",
        "**Thông tin hộ dân bị thiệt hại:**",
        "Họ tên: Nguyễn Văn An",
        "Địa chỉ: 45 Trần Hưng Đạo, Phường Hải Thành, TP Đồng Hới",
        "Số CCCD: 001234567890",
        "",
        "**Sự kiện thiên tai:**",
        "Loại thiên tai: Lũ lụt do hoàn lưu bão số 4 năm 2024",
        "Thời gian xảy ra: 10/10/2024 đến 15/10/2024",
        "Mức độ: Nghiêm trọng (nước ngập 1.2m tại khu vực nhà ở)",
        "",
        "**Thiệt hại ghi nhận:**",
        "- Nhà ở bị ngập hoàn toàn, tường nứt, nền hư hỏng",
        "- Toàn bộ đồ dùng sinh hoạt bị hư hỏng",
        "- Ước tính thiệt hại: 45,000,000 VND",
        "",
        "---",
        "Tài liệu đính kèm: Ảnh hiện trường, biên bản địa phương",
        "",
        "Đồng Hới, ngày 16/10/2024",
        "Chủ tịch UBND xã                     Xác nhận của Phòng LĐTB&XH",
        "[Dấu đỏ UBND]",
    ], "BIÊN BẢN XÁC NHẬN THIỆT HẠI THIÊN TAI")

    # ── 6. CLAIM THIÊN TAI — BÃO (approve) ───────────────────────────────────
    make_pdf("disaster_storm_hatinh_approve.pdf", [
        "UBND TỈNH HÀ TĨNH",
        "Phòng Quản lý Thiên tai — Ban Chỉ huy PCTT",
        "---",
        "",
        "**BIÊN BẢN THIỆT HẠI DO BÃO SỐ 4 NĂM 2024**",
        "",
        "Họ tên chủ hộ: Phạm Thị Hoa",
        "Địa chỉ: 78 Nguyễn Công Trứ, TP Hà Tĩnh",
        "Số CCCD: 038234567890",
        "",
        "**Sự kiện:**",
        "Loại thiên tai: Bão số 4/2024 (tên quốc tế: Typhoon Yagi)",
        "Thời gian: 06/09/2024 đến 08/09/2024",
        "Sức gió tối đa tại Hà Tĩnh: cấp 12-13",
        "",
        "**Thiệt hại:**",
        "- Mái ngói nhà chính bị tốc hoàn toàn (60m2)",
        "- Tường rào bị đổ (15m)",
        "- Cây xanh đổ vào công trình phụ",
        "- Ô tô bị cây đổ trúng",
        "",
        "Tổng thiệt hại ước tính: 28,000,000 VND",
        "",
        "---",
        "Hà Tĩnh, ngày 09/09/2024",
        "Trưởng Ban Chỉ huy PCTT tỉnh",
        "[Dấu đỏ và chữ ký]",
    ], "BIÊN BẢN THIỆT HẠI DO BÃO")

    # ── 7. HÓA ĐƠN NHA KHOA ─────────────────────────────────────────────────
    make_pdf("invoice_nha_khoa_approve.pdf", [
        "Địa chỉ: 25 Hoàng Diệu, Quận 4, TP Hồ Chí Minh",
        "Giấy phép hoạt động: 12345/GP-SYT",
        "ĐT: 028.1234.5678",
        "---",
        "",
        "**PHIẾU THU TIỀN DỊCH VỤ NHA KHOA**",
        f"Ngày khám: {datetime.now().strftime('%d/%m/%Y')}",
        "",
        "Bệnh nhân: Lê Thị Thu",
        "Ngày sinh: 20/06/1995",
        "SĐT: 0987.654.321",
        "",
        "Bác sĩ: BS. CKI Lê Hoàng Nam — Chuyên khoa Răng Hàm Mặt",
        "",
        "---",
        "**DỊCH VỤ:**",
        "",
        "1. Trám răng số 6 (răng sâu độ 3)         900,000 VND",
        "2. Cạo vôi răng toàn hàm                   450,000 VND",
        "3. X-quang răng panorama                    200,000 VND",
        "",
        "---",
        "**TỔNG CỘNG: 1,550,000 VND**",
        "Hình thức: Chuyển khoản",
        "",
        "Bác sĩ ký xác nhận: [BS. Lê Hoàng Nam]",
        "[Dấu đỏ Nha khoa Smile]",
    ], "PHÒNG KHÁM NHA KHOA SMILE")

    # ── 8. HỢP ĐỒNG BẢO HIỂM ─────────────────────────────────────────────────
    make_pdf("insurance_policy_disaster.pdf", [
        "Số hợp đồng: BH-THIEN-TAI-2024-001234",
        "Ngày phát hành: 01/01/2024",
        "---",
        "",
        "**HỢP ĐỒNG BẢO HIỂM THIÊN TAI**",
        "",
        "**BÊN BẢO HIỂM:** ClaimFlow Insurance Co., Ltd",
        "MST: 0123456789 | Giấy phép: 987/GP-BTC",
        "",
        "**BÊN ĐƯỢC BẢO HIỂM:**",
        "Họ tên: Nguyễn Văn An",
        "CCCD: 001234567890",
        "Địa chỉ: 45 Trần Hưng Đạo, TP Đồng Hới, Quảng Bình",
        "",
        "---",
        "**ĐIỀU KHOẢN BẢO HIỂM:**",
        "",
        "Loại bảo hiểm: Bảo hiểm thiên tai toàn diện",
        "Thời hạn: 01/01/2024 - 31/12/2024",
        "Phí bảo hiểm: 3,500,000 VND/năm",
        "",
        "Phạm vi bảo hiểm:",
        "- Thiệt hại nhà ở do bão lũ: tối đa 100,000,000 VND",
        "- Thiệt hại tài sản do lũ: tối đa 50,000,000 VND",
        "- Hỗ trợ di dời khẩn cấp: tối đa 10,000,000 VND",
        "",
        "---",
        "Hệ số rủi ro khu vực Quảng Bình: 1.3 (vùng rủi ro cao)",
        "",
        "Đại diện bên bảo hiểm: [Ký tên và đóng dấu]",
        "Người được bảo hiểm: [Nguyễn Văn An - Ký tên]",
    ], "HỢP ĐỒNG BẢO HIỂM THIÊN TAI")

    print(f"\n{'='*50}")
    print(f"✅ Generated {8} documents in {OUTPUT_DIR}/")
    print(f"{'='*50}")
    print("""
📋 Test scenarios:
  cccd_nguyen_van_an.pdf         → OCR CCCD (Quảng Bình)
  cccd_le_thi_thu.pdf            → OCR CCCD (HCM)
  invoice_viem_phoi_approve.pdf  → Medical claim → APPROVE (J18.1)
  invoice_tham_my_reject.pdf     → Medical claim → REJECT (thẩm mỹ)
  disaster_flood_quangbinh_approve.pdf → Disaster flood → APPROVE
  disaster_storm_hatinh_approve.pdf    → Disaster storm → APPROVE
  invoice_nha_khoa_approve.pdf   → Dental claim → APPROVE
  insurance_policy_disaster.pdf  → Insurance policy document
    """)


if __name__ == "__main__":
    run()

import os
import uuid
from datetime import datetime, date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="QC SpecChecker", page_icon="🍎", layout="wide")

# ---------------------------------------------------------------------------
# 기본 데이터
# ---------------------------------------------------------------------------
DEFAULT_PRODUCTS = [
    "수분크림 A", "수분크림 B", "클렌징폼 A", "클렌징폼 B",
    "토너 A", "토너 B", "에센스 A", "에센스 B", "선크림 A", "선크림 B",
]

DEFAULT_SPECS = [
    {"id": "s1", "product": "수분크림 A", "name": "pH", "unit": "-", "min": 5.0, "max": 6.5},
    {"id": "s2", "product": "수분크림 A", "name": "점도", "unit": "mPa·s", "min": 3000, "max": 8000},
    {"id": "s3", "product": "수분크림 B", "name": "pH", "unit": "-", "min": 5.0, "max": 6.5},
    {"id": "s4", "product": "수분크림 B", "name": "점도", "unit": "mPa·s", "min": 4000, "max": 9000},
    {"id": "s5", "product": "클렌징폼 A", "name": "pH", "unit": "-", "min": 6.0, "max": 8.0},
    {"id": "s6", "product": "클렌징폼 A", "name": "총호기성생균수", "unit": "CFU/g", "min": 0, "max": 100},
    {"id": "s7", "product": "클렌징폼 B", "name": "pH", "unit": "-", "min": 6.0, "max": 8.0},
    {"id": "s8", "product": "클렌징폼 B", "name": "총호기성생균수", "unit": "CFU/g", "min": 0, "max": 100},
    {"id": "s9", "product": "토너 A", "name": "pH", "unit": "-", "min": 4.5, "max": 6.0},
    {"id": "s10", "product": "토너 A", "name": "점도", "unit": "mPa·s", "min": 50, "max": 300},
    {"id": "s11", "product": "토너 B", "name": "pH", "unit": "-", "min": 4.5, "max": 6.0},
    {"id": "s12", "product": "토너 B", "name": "점도", "unit": "mPa·s", "min": 50, "max": 300},
    {"id": "s13", "product": "에센스 A", "name": "pH", "unit": "-", "min": 5.0, "max": 6.5},
    {"id": "s14", "product": "에센스 A", "name": "점도", "unit": "mPa·s", "min": 2000, "max": 5000},
    {"id": "s15", "product": "에센스 B", "name": "pH", "unit": "-", "min": 5.0, "max": 6.5},
    {"id": "s16", "product": "에센스 B", "name": "점도", "unit": "mPa·s", "min": 2000, "max": 5000},
    {"id": "s17", "product": "선크림 A", "name": "pH", "unit": "-", "min": 6.0, "max": 7.5},
    {"id": "s18", "product": "선크림 A", "name": "총호기성생균수", "unit": "CFU/g", "min": 0, "max": 100},
    {"id": "s19", "product": "선크림 B", "name": "pH", "unit": "-", "min": 6.0, "max": 7.5},
    {"id": "s20", "product": "선크림 B", "name": "총호기성생균수", "unit": "CFU/g", "min": 0, "max": 100},
]

VERDICT_MAP = {"합격": "pass", "부적합": "fail", "pass": "pass", "fail": "fail"}
CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_data.csv")


def build_default_results():
    """sample_data.csv가 있으면 그 값을 시드로 사용하고, 없으면 내장 기본값을 사용합니다."""
    seed_rows = []
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        for _, row in df.iterrows():
            seed_rows.append({
                "product": row["제품명"],
                "batch": row["배치번호"],
                "spec_name": row["검사항목"],
                "spec_unit": row["단위"],
                "spec_min": row["규격하한"],
                "spec_max": row["규격상한"],
                "value": row["측정값"],
                "verdict": VERDICT_MAP.get(str(row["판정"]).strip(), "pass"),
            })
    else:
        seed_rows = [
            {"product": "수분크림 A", "batch": "B2607-01", "spec_name": "pH", "spec_unit": "-", "spec_min": 5.0, "spec_max": 6.5, "value": 6.2, "verdict": "pass"},
            {"product": "수분크림 A", "batch": "B2607-02", "spec_name": "점도", "spec_unit": "mPa·s", "spec_min": 3000, "spec_max": 8000, "value": 8600, "verdict": "fail"},
            {"product": "수분크림 B", "batch": "B2607-03", "spec_name": "pH", "spec_unit": "-", "spec_min": 5.0, "spec_max": 6.5, "value": 5.8, "verdict": "pass"},
            {"product": "클렌징폼 A", "batch": "B2607-04", "spec_name": "총호기성생균수", "spec_unit": "CFU/g", "spec_min": 0, "spec_max": 100, "value": 45, "verdict": "pass"},
            {"product": "클렌징폼 A", "batch": "B2607-05", "spec_name": "총호기성생균수", "spec_unit": "CFU/g", "spec_min": 0, "spec_max": 100, "value": 180, "verdict": "fail"},
            {"product": "클렌징폼 B", "batch": "B2607-06", "spec_name": "pH", "spec_unit": "-", "spec_min": 6.0, "spec_max": 8.0, "value": 7.2, "verdict": "pass"},
            {"product": "토너 A", "batch": "B2607-07", "spec_name": "pH", "spec_unit": "-", "spec_min": 4.5, "spec_max": 6.0, "value": 4.9, "verdict": "pass"},
            {"product": "토너 B", "batch": "B2607-08", "spec_name": "점도", "spec_unit": "mPa·s", "spec_min": 100, "spec_max": 500, "value": 350, "verdict": "pass"},
            {"product": "에센스 A", "batch": "B2607-09", "spec_name": "점도", "spec_unit": "mPa·s", "spec_min": 2000, "spec_max": 5000, "value": 5200, "verdict": "fail"},
            {"product": "선크림 A", "batch": "B2607-10", "spec_name": "총호기성생균수", "spec_unit": "CFU/g", "spec_min": 0, "spec_max": 100, "value": 60, "verdict": "pass"},
        ]

    now = datetime.now()
    results = []
    n = len(seed_rows)
    for i, r in enumerate(seed_rows):
        results.append({
            **r,
            "id": f"r-seed-{i}",
            "resolved": False,
            "date": now,
        })
    return results


# ---------------------------------------------------------------------------
# 세션 상태 초기화 (같은 세션 동안만 유지되며, 새로고침 시 초기화됩니다)
# ---------------------------------------------------------------------------
if "products" not in st.session_state:
    st.session_state.products = DEFAULT_PRODUCTS.copy()
if "specs" not in st.session_state:
    st.session_state.specs = [s.copy() for s in DEFAULT_SPECS]
if "results" not in st.session_state:
    st.session_state.results = build_default_results()
if "show_fail_only" not in st.session_state:
    st.session_state.show_fail_only = False


def ensure_product(name: str):
    name = name.strip()
    if not name:
        return
    exists = any(p.lower() == name.lower() for p in st.session_state.products)
    if not exists:
        st.session_state.products.append(name)


def find_spec(product: str, item_name: str):
    for s in st.session_state.specs:
        if s["product"].lower() == product.lower() and s["name"].lower() == item_name.lower():
            return s
    return None


def judge(value: float, spec: dict) -> str:
    return "pass" if spec["min"] <= value <= spec["max"] else "fail"


def compute_fail_counts():
    """제품+항목 기준으로 누적 부적합 발생 순번을 계산합니다."""
    counts = {}
    group_tally = {}
    for r in sorted(st.session_state.results, key=lambda x: x["date"]):
        if r["verdict"] != "fail":
            continue
        key = (r["product"].lower(), r["spec_name"].lower())
        group_tally[key] = group_tally.get(key, 0) + 1
        counts[r["id"]] = group_tally[key]
    return counts


# ---------------------------------------------------------------------------
# 헤더
# ---------------------------------------------------------------------------
col_title, col_logo = st.columns([6, 1])
with col_title:
    st.title("🍎 QC SpecChecker")
    st.caption("제품별 스펙만 등록해두면, 검사 결과 입력 즉시 합격/부적합을 판정하고 이상치를 알려드려요.")

st.divider()

# ---------------------------------------------------------------------------
# 요약 카드
# ---------------------------------------------------------------------------
today = date.today()
todays = [r for r in st.session_state.results if r["date"].date() == today]
total_today = len(todays)
pass_today = len([r for r in todays if r["verdict"] == "pass"])
fail_today = len([r for r in todays if r["verdict"] == "fail"])

c1, c2, c3 = st.columns(3)
c1.metric("오늘 검사", total_today)
c2.metric("합격", pass_today)
with c3:
    st.metric("부적합", fail_today)
    if st.button("부적합만 모아보기" if not st.session_state.show_fail_only else "전체보기", key="toggle_fail"):
        st.session_state.show_fail_only = not st.session_state.show_fail_only
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# 검사 결과 입력
# ---------------------------------------------------------------------------
st.subheader("검사 결과 입력")

product_options = ["직접 입력"] + st.session_state.products
with st.form("result_form", clear_on_submit=True):
    fc1, fc2 = st.columns(2)
    with fc1:
        product_choice = st.selectbox("제품명", product_options, key="product_choice")
        product_free = st.text_input("새 제품명 입력", key="product_free") if product_choice == "직접 입력" else ""
    with fc2:
        batch_no = st.text_input("배치번호", placeholder="예: B2607-01")

    product_name = product_free.strip() if product_choice == "직접 입력" else product_choice
    matched_specs = [s for s in st.session_state.specs if s["product"].lower() == product_name.lower()]
    item_source = matched_specs if matched_specs else st.session_state.specs
    item_names = sorted({s["name"] for s in item_source}) or ["등록된 항목 없음"]

    fc3, fc4 = st.columns(2)
    with fc3:
        item_name = st.selectbox("검사항목", item_names)
    with fc4:
        measured_value = st.number_input("측정값", value=0.0, format="%.4f")

    submitted = st.form_submit_button("결과 등록", type="primary")

if submitted:
    if not product_name or item_name == "등록된 항목 없음":
        st.error("제품명과 검사항목을 확인해 주세요.")
    else:
        spec = find_spec(product_name, item_name)
        if not spec:
            st.error('해당 제품에 등록된 검사항목이 아닙니다. "제품별 검사항목 스펙 관리"에서 먼저 스펙을 등록해 주세요.')
        else:
            ensure_product(product_name)
            verdict = judge(measured_value, spec)
            new_row = {
                "id": f"r-{uuid.uuid4().hex[:10]}",
                "date": datetime.now(),
                "product": product_name,
                "batch": batch_no.strip(),
                "spec_name": spec["name"],
                "spec_unit": spec["unit"],
                "spec_min": spec["min"],
                "spec_max": spec["max"],
                "value": measured_value,
                "verdict": verdict,
                "resolved": False,
            }
            st.session_state.results.append(new_row)

            if verdict == "pass":
                for r in st.session_state.results:
                    if (r["verdict"] == "fail" and not r["resolved"]
                            and r["product"].lower() == product_name.lower()
                            and r["spec_name"].lower() == spec["name"].lower()):
                        r["resolved"] = True

            if verdict == "pass":
                st.success(f"합격 판정입니다. (측정값: {measured_value}, 규격: {spec['min']}~{spec['max']} {spec['unit']})")
            else:
                st.error(f"부적합 판정입니다. (측정값: {measured_value}, 규격: {spec['min']}~{spec['max']} {spec['unit']})")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# 제품별 검사항목 스펙 관리
# ---------------------------------------------------------------------------
with st.expander("제품별 검사항목 스펙(규격) 관리"):
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    with sc1:
        spec_product_choice = st.selectbox("제품명", ["직접 입력"] + st.session_state.products, key="spec_product_choice")
        spec_product_free = st.text_input("새 제품명", key="spec_product_free") if spec_product_choice == "직접 입력" else ""
    with sc2:
        spec_name = st.text_input("항목명", placeholder="예: pH", key="spec_name_input")
    with sc3:
        spec_unit = st.text_input("단위", placeholder="예: -, mPa·s, CFU/g", key="spec_unit_input")
    with sc4:
        spec_min = st.number_input("하한값", value=0.0, format="%.4f", key="spec_min_input")
    with sc5:
        spec_max = st.number_input("상한값", value=0.0, format="%.4f", key="spec_max_input")

    spec_product_name = spec_product_free.strip() if spec_product_choice == "직접 입력" else spec_product_choice

    if st.button("스펙 추가"):
        if not spec_product_name or not spec_name.strip():
            st.error("제품명과 항목명을 입력해 주세요.")
        elif spec_min > spec_max:
            st.error("하한값이 상한값보다 클 수 없습니다.")
        else:
            ensure_product(spec_product_name)
            st.session_state.specs.append({
                "id": f"s-{uuid.uuid4().hex[:10]}",
                "product": spec_product_name,
                "name": spec_name.strip(),
                "unit": spec_unit.strip(),
                "min": spec_min,
                "max": spec_max,
            })
            st.success("스펙이 추가되었습니다.")
            st.rerun()

    st.markdown("---")
    if not st.session_state.specs:
        st.caption("등록된 스펙이 없습니다.")
    else:
        by_product = {}
        for s in st.session_state.specs:
            by_product.setdefault(s["product"], []).append(s)
        for product, spec_list in by_product.items():
            st.markdown(f"**{product}**")
            for s in spec_list:
                row_c1, row_c2 = st.columns([5, 1])
                row_c1.write(f"{s['name']} | {s['min']} ~ {s['max']} {s['unit']}")
                if row_c2.button("삭제", key=f"del_{s['id']}"):
                    st.session_state.specs = [x for x in st.session_state.specs if x["id"] != s["id"]]
                    st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# 검사 결과 이력
# ---------------------------------------------------------------------------
st.subheader("검사 결과 이력")

if st.session_state.show_fail_only:
    st.info("부적합 항목만 보고 있습니다.")

source = [r for r in st.session_state.results if r["verdict"] == "fail"] if st.session_state.show_fail_only else st.session_state.results

if not source:
    st.caption("부적합 항목이 없습니다." if st.session_state.show_fail_only else "등록된 결과가 없습니다.")
else:
    fail_counts = compute_fail_counts()
    rows = []
    for r in sorted(source, key=lambda x: x["date"], reverse=True):
        if r["verdict"] == "pass":
            label = "합격"
        else:
            fail_no = fail_counts.get(r["id"], 1)
            base = f"부적합({fail_no})" if fail_no > 1 else "부적합"
            label = f"{base} (재검사 통과)" if r["resolved"] else base
        rows.append({
            "일시": r["date"].strftime("%m/%d %H:%M"),
            "제품명": r["product"],
            "배치번호": r["batch"],
            "항목": f"{r['spec_name']}" + (f" ({r['spec_unit']})" if r["spec_unit"] and r["spec_unit"] != "-" else ""),
            "측정값": r["value"],
            "규격": f"{r['spec_min']}~{r['spec_max']}",
            "판정": label,
        })
    result_df = pd.DataFrame(rows)
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    csv_bytes = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("결과 CSV 다운로드", data=csv_bytes, file_name="qc_results.csv", mime="text/csv")

st.caption("⚠️ 이 앱의 데이터는 세션 동안만 유지됩니다. 새로고침하거나 앱이 재시작되면 초기화됩니다.")

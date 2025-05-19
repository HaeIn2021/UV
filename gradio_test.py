#!/usr/bin/env python
# 환경 데이터 처리 예제
import gradio as gr
import pandas as pd
import plotly.express as px

def process_air_quality_data(*args, **kwargs):
    """
    여러 도시의 대기질 데이터를 처리하고 분석하는 함수
    *args: 각 도시의 대기질 데이터 (PM10, PM2.5, O3 등)
    **kwargs: 분석 옵션 (임계값, 가중치 등)
    """
    if not args:
        return "처리할 데이터가 없습니다."
    
    results = {}
    threshold = kwargs.get('threshold', 50)  # 기본 임계값 50
    weight_pm10 = kwargs.get('pm10_weight', 0.6)  # PM10 가중치
    weight_pm25 = kwargs.get('pm25_weight', 0.4)  # PM2.5 가중치
    
    for city_data in args:
        city_name = city_data.get('도시')
        if not city_name:
            continue
            
        # 대기질 지수 계산
        pm10 = city_data.get('PM10', 0)
        pm25 = city_data.get('PM2.5', 0)
        o3 = city_data.get('O3', 0)
        
        # 가중 평균 계산
        weighted_score = (pm10 * weight_pm10 + pm25 * weight_pm25)
        
        # 상태 판단
        status = "좋음"
        if weighted_score > threshold * 1.5:
            status = "나쁨"
        elif weighted_score > threshold:
            status = "보통"
            
        results[city_name] = {
            'PM10': pm10,
            'PM2.5': pm25,
            'O3': o3,
            '가중점수': round(weighted_score, 2),
            '상태': status
        }
    
    return results

# Gradio 함수
def analyze_air_quality(threshold, pm10_weight, pm25_weight):
    # 샘플 데이터 (고정값)
    cities_data = [
        {'도시': '서울', 'PM10': 45, 'PM2.5': 22, 'O3': 0.03},
        {'도시': '부산', 'PM10': 38, 'PM2.5': 18, 'O3': 0.02},
        {'도시': '인천', 'PM10': 51, 'PM2.5': 26, 'O3': 0.04},
        {'도시': '대구', 'PM10': 42, 'PM2.5': 20, 'O3': 0.03},
        {'도시': '광주', 'PM10': 40, 'PM2.5': 19, 'O3': 0.02}
    ]
    
    # 대기질 데이터 처리
    results = process_air_quality_data(
        *cities_data,
        threshold=threshold,
        pm10_weight=pm10_weight, 
        pm25_weight=pm25_weight
    )
    
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame.from_dict(results, orient='index')
    df = df.reset_index().rename(columns={'index': '도시'})
    
    # 막대 그래프 생성
    fig1 = px.bar(df, x='도시', y=['PM10', 'PM2.5'], barmode='group',
                  title='도시별 미세먼지 농도')
    
    # 가중점수 차트 생성
    fig2 = px.bar(df, x='도시', y='가중점수', color='상태',
                  color_discrete_map={'좋음': 'green', '보통': 'yellow', '나쁨': 'red'},
                  title='도시별 대기질 가중점수')
    
    # 표, 그래프 반환
    return df, fig1, fig2

# Gradio 인터페이스 설정
with gr.Blocks(title="대기질 분석 대시보드") as demo:
    gr.Markdown("# 대기질 분석 대시보드")
    gr.Markdown("### 도시별 대기질 데이터 분석")
    
    with gr.Row():
        with gr.Column(scale=1):
            threshold = gr.Slider(minimum=20, maximum=80, value=50, step=1, label="임계값 설정")
            pm10_weight = gr.Slider(minimum=0.0, maximum=1.0, value=0.6, step=0.1, label="PM10 가중치")
            pm25_weight = gr.Slider(minimum=0.0, maximum=1.0, value=0.4, step=0.1, label="PM2.5 가중치")
            analyze_button = gr.Button("대기질 분석하기")
    
    with gr.Row():
        results_table = gr.DataFrame(label="대기질 분석 결과")
    
    with gr.Row():
        with gr.Column():
            pm_chart = gr.Plot(label="도시별 미세먼지 농도")
        with gr.Column():
            score_chart = gr.Plot(label="도시별 대기질 가중점수")
    
    analyze_button.click(
        fn=analyze_air_quality,
        inputs=[threshold, pm10_weight, pm25_weight],
        outputs=[results_table, pm_chart, score_chart]
    )
    
    # 페이지 로드 시 기본값으로 결과 표시
    demo.load(
        fn=analyze_air_quality,
        inputs=[gr.Slider(value=50), gr.Slider(value=0.6), gr.Slider(value=0.4)],
        outputs=[results_table, pm_chart, score_chart]
    )

# Gradio 앱 실행
if __name__ == "__main__":
    demo.launch(share=True)  # share=True는 공개 URL 생성
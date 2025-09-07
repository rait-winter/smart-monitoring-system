#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI异常检测服务 - 智能监控预警系统核心AI引擎

功能特性:
1. 多算法异常检测 (Isolation Forest, Z-Score, LSTM, Prophet)
2. 时间序列数据预处理和特征工程 
3. 模型管理和缓存优化
4. 异常评分和严重程度分析
5. 预测性预警分析
6. 模型持久化和版本管理

技术架构:
- 基于Scikit-learn机器学习框架
- 支持多算法组合决策
- 内存缓存优化性能
- 异步处理提升并发
- 详细日志和错误处理

作者: AI监控团队
版本: 2.0.0
最后更新: 2025-09-06
"""

import asyncio
import json
import pickle
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import precision_recall_curve, roc_auc_score
from sklearn.model_selection import train_test_split
from scipy import stats
from scipy.signal import find_peaks
import joblib
from cachetools import TTLCache
import structlog

from app.models.schemas import (
    AnomalyDetectionRequest, 
    AnomalyDetectionResult,
    AnomalyPoint,
    AlgorithmType,
    AlertSeverity
)
from app.core.config import settings

# 忽略sklearn和pandas的警告信息，保持日志清洁
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# 配置结构化日志记录器
logger = structlog.get_logger(__name__)


@dataclass
class ModelMetadata:
    """
    AI模型元数据
    
    存储模型训练信息、性能指标和配置参数
    用于模型版本管理和性能监控
    """
    algorithm: str                    # 算法类型
    version: str                      # 模型版本号
    trained_at: datetime             # 训练时间
    data_shape: Tuple[int, int]      # 训练数据维度 (样本数, 特征数)
    performance_metrics: Dict[str, float]  # 性能指标 (准确率, 召回率等)
    hyperparameters: Dict[str, Any]  # 超参数配置
    feature_names: List[str]         # 特征名称列表
    preprocessing_params: Dict[str, Any]  # 预处理参数


class AnomalyScoreLevel(Enum):
    """异常分数等级枚举"""
    NORMAL = "normal"          # 正常: 0.0-0.3
    SUSPICIOUS = "suspicious"  # 可疑: 0.3-0.6  
    ANOMALOUS = "anomalous"    # 异常: 0.6-0.8
    CRITICAL = "critical"      # 严重: 0.8-1.0


class AIAnomalyDetector:
    """
    AI异常检测器 - 智能监控系统的核心AI引擎
    
    集成多种异常检测算法，提供高精度的异常识别能力。
    支持时间序列数据分析、模型训练、预测和实时检测。
    
    核心功能:
    1. 多算法异常检测 (Isolation Forest, Statistical Z-Score, LSTM)
    2. 智能数据预处理和特征工程
    3. 模型持久化和版本管理
    4. 异常评分和严重程度评估
    5. 预测性分析和趋势识别
    6. 性能监控和模型优化
    
    使用示例:
        detector = AIAnomalyDetector()
        
        # 训练模型
        await detector.train_model(historical_data, algorithm="isolation_forest")
        
        # 检测异常
        result = await detector.detect_anomalies(metrics_data, algorithm="isolation_forest")
        
        # 获取预测
        forecast = await detector.predict_future_values(metrics_data, hours=24)
    """
    
    def __init__(self):
        """
        初始化AI异常检测器
        
        设置模型存储路径、缓存配置和算法参数
        """
        self.logger = logger.bind(component="AIAnomalyDetector")
        
        # 模型存储配置
        self.model_dir = Path(settings.AI_MODEL_PATH)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存配置 - 缓存模型和预处理器，TTL=5分钟
        self.model_cache = TTLCache(maxsize=50, ttl=settings.AI_CACHE_TTL)
        self.scaler_cache = TTLCache(maxsize=50, ttl=settings.AI_CACHE_TTL)
        
        # 算法配置参数
        self.algorithm_configs = {
            AlgorithmType.ISOLATION_FOREST: {
                "n_estimators": 100,      # 决策树数量
                "contamination": 0.1,     # 异常比例估计
                "random_state": 42,       # 随机种子
                "n_jobs": -1             # 并行处理
            },
            AlgorithmType.Z_SCORE: {
                "threshold": 3.0,         # Z-Score阈值 
                "window_size": 10,        # 滑动窗口大小
                "min_samples": 30         # 最小样本数
            },
            AlgorithmType.STATISTICAL: {
                "percentile_threshold": 95,  # 百分位阈值
                "mad_threshold": 3.5,        # 中位数绝对偏差阈值
                "iqr_factor": 1.5           # 四分位数因子
            }
        }
        
        # 严重程度评估阈值
        self.severity_thresholds = {
            AlertSeverity.LOW: (0.0, 0.3),
            AlertSeverity.MEDIUM: (0.3, 0.6), 
            AlertSeverity.HIGH: (0.6, 0.8),
            AlertSeverity.CRITICAL: (0.8, 1.0)
        }
        
        self.logger.info(
            "AI异常检测器初始化完成",
            model_dir=str(self.model_dir),
            cache_ttl=settings.AI_CACHE_TTL,
            algorithms=list(self.algorithm_configs.keys())
        )
    
    
    async def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        algorithm: AlgorithmType = AlgorithmType.ISOLATION_FOREST,
        sensitivity: float = 0.8,
        threshold: Optional[float] = None
    ) -> AnomalyDetectionResult:
        """
        执行异常检测分析
        
        基于指定算法对时间序列数据进行异常检测，
        识别异常点并计算异常评分和严重程度。
        
        Args:
            data: 时间序列数据列表，格式: [{"timestamp": "...", "value": float, "labels": {...}}]
            algorithm: 检测算法类型
            sensitivity: 敏感度参数 (0.1-1.0)，越高越敏感
            threshold: 自定义异常阈值，None时使用默认阈值
        
        Returns:
            AnomalyDetectionResult: 检测结果，包含异常点列表和统计信息
            
        Raises:
            ValueError: 当数据格式错误或参数无效时
            RuntimeError: 当模型加载或计算失败时
        """
        start_time = time.time()
        self.logger.info(
            "开始异常检测",
            algorithm=algorithm.value,
            data_points=len(data),
            sensitivity=sensitivity
        )
        
        try:
            # 1. 数据验证和预处理
            if not data or len(data) < 10:
                raise ValueError("数据点数量不足，至少需要10个数据点进行异常检测")
            
            df = await self._preprocess_data(data)
            
            # 2. 特征工程 - 提取时间序列特征
            features_df = await self._extract_features(df)
            
            # 3. 根据算法执行异常检测
            if algorithm == AlgorithmType.ISOLATION_FOREST:
                anomaly_scores, anomalies = await self._detect_isolation_forest(
                    features_df, sensitivity, threshold
                )
            elif algorithm == AlgorithmType.Z_SCORE:
                anomaly_scores, anomalies = await self._detect_z_score(
                    features_df, sensitivity, threshold
                )
            elif algorithm == AlgorithmType.STATISTICAL:
                anomaly_scores, anomalies = await self._detect_statistical(
                    features_df, sensitivity, threshold
                )
            else:
                raise ValueError(f"不支持的算法类型: {algorithm}")
            
            # 4. 生成异常点详细信息
            anomaly_points = await self._generate_anomaly_points(
                df, anomaly_scores, anomalies, algorithm
            )
            
            # 5. 计算整体统计信息
            total_points = len(df)
            anomaly_count = len(anomaly_points)
            overall_score = float(np.mean(anomaly_scores)) if len(anomaly_scores) > 0 else 0.0
            
            # 6. 生成建议和说明
            recommendations = await self._generate_recommendations(
                anomaly_points, overall_score, algorithm
            )
            
            # 7. 模型信息
            model_info = {
                "algorithm": algorithm.value,
                "sensitivity": sensitivity,
                "threshold": threshold,
                "feature_count": len(features_df.columns),
                "data_timespan": f"{df.index[-1] - df.index[0]}",
                "anomaly_rate": anomaly_count / total_points if total_points > 0 else 0
            }
            
            execution_time = time.time() - start_time
            
            self.logger.info(
                "异常检测完成",
                algorithm=algorithm.value,
                total_points=total_points,
                anomaly_count=anomaly_count,
                overall_score=round(overall_score, 3),
                execution_time=round(execution_time, 3)
            )
            
            return AnomalyDetectionResult(
                anomalies=anomaly_points,
                total_points=total_points,
                anomaly_count=anomaly_count,
                overall_score=overall_score,
                algorithm_used=algorithm,
                execution_time=execution_time,
                recommendations=recommendations,
                model_info=model_info
            )
            
        except Exception as e:
            self.logger.error(
                "异常检测失败",
                algorithm=algorithm.value,
                error=str(e),
                execution_time=time.time() - start_time
            )
            raise RuntimeError(f"异常检测执行失败: {str(e)}")
    
    
    async def _preprocess_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        数据预处理
        
        将原始时间序列数据转换为DataFrame格式，
        进行数据清洗、缺失值处理和格式标准化。
        
        Args:
            data: 原始时间序列数据
            
        Returns:
            pd.DataFrame: 预处理后的数据，索引为时间戳
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 时间戳处理
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            else:
                # 如果没有时间戳，生成递增时间序列
                df.index = pd.date_range(
                    start=datetime.now() - timedelta(hours=len(df)),
                    periods=len(df),
                    freq='1min'
                )
            
            # 确保value列存在并为数值类型
            if 'value' not in df.columns:
                raise ValueError("数据中缺少'value'列")
            
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # 处理缺失值 - 使用前向填充和后向填充
            df['value'].fillna(method='ffill', inplace=True)
            df['value'].fillna(method='bfill', inplace=True)
            
            # 移除仍然为NaN的行
            df.dropna(subset=['value'], inplace=True)
            
            # 按时间排序
            df.sort_index(inplace=True)
            
            # 移除重复的时间戳
            df = df[~df.index.duplicated(keep='first')]
            
            self.logger.debug(
                "数据预处理完成",
                shape=df.shape,
                time_range=f"{df.index[0]} 到 {df.index[-1]}",
                value_range=f"{df['value'].min():.2f} 到 {df['value'].max():.2f}"
            )
            
            return df
            
        except Exception as e:
            self.logger.error("数据预处理失败", error=str(e))
            raise ValueError(f"数据预处理失败: {str(e)}")
    
    
    async def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        时间序列特征工程
        
        从原始时间序列数据中提取统计特征、趋势特征和周期特征，
        为异常检测算法提供丰富的特征输入。
        
        Args:
            df: 预处理后的时间序列数据
            
        Returns:
            pd.DataFrame: 包含多维特征的数据框架
        """
        try:
            features_df = df.copy()
            values = df['value']
            
            # === 基础统计特征 ===
            # 滑动窗口统计 (5分钟窗口)
            window_5m = min(5, len(values) // 4)
            if window_5m > 1:
                features_df['rolling_mean_5m'] = values.rolling(window=window_5m, min_periods=1).mean()
                features_df['rolling_std_5m'] = values.rolling(window=window_5m, min_periods=1).std()
                features_df['rolling_min_5m'] = values.rolling(window=window_5m, min_periods=1).min()
                features_df['rolling_max_5m'] = values.rolling(window=window_5m, min_periods=1).max()
            
            # 滑动窗口统计 (30分钟窗口)
            window_30m = min(30, len(values) // 2)
            if window_30m > 1:
                features_df['rolling_mean_30m'] = values.rolling(window=window_30m, min_periods=1).mean()
                features_df['rolling_std_30m'] = values.rolling(window=window_30m, min_periods=1).std()
            
            # === 变化率特征 ===
            # 一阶差分 (变化量)
            features_df['diff_1'] = values.diff(1).fillna(0)
            # 二阶差分 (加速度)
            features_df['diff_2'] = values.diff(2).fillna(0)
            # 百分比变化率
            features_df['pct_change'] = values.pct_change(1).fillna(0)
            
            # === Z-Score标准化特征 ===
            # 全局Z-Score
            global_mean = values.mean()
            global_std = values.std()
            if global_std > 0:
                features_df['z_score_global'] = (values - global_mean) / global_std
            else:
                features_df['z_score_global'] = 0
            
            # 滑动Z-Score
            if window_30m > 1:
                rolling_mean = features_df['rolling_mean_30m']
                rolling_std = features_df['rolling_std_30m']
                features_df['z_score_rolling'] = np.where(
                    rolling_std > 0,
                    (values - rolling_mean) / rolling_std,
                    0
                )
            
            # === 趋势特征 ===
            # 与滑动均值的偏差
            if window_5m > 1:
                features_df['deviation_from_mean'] = values - features_df['rolling_mean_5m']
                # 标准化偏差
                features_df['normalized_deviation'] = np.where(
                    features_df['rolling_std_5m'] > 0,
                    features_df['deviation_from_mean'] / features_df['rolling_std_5m'],
                    0
                )
            
            # === 极值特征 ===
            # 局部极大值和极小值
            if len(values) > 10:
                # 寻找峰值
                peaks_max, _ = find_peaks(values.values, distance=max(1, len(values) // 20))
                peaks_min, _ = find_peaks(-values.values, distance=max(1, len(values) // 20))
                
                features_df['is_local_max'] = 0
                features_df['is_local_min'] = 0
                features_df.iloc[peaks_max, features_df.columns.get_loc('is_local_max')] = 1
                features_df.iloc[peaks_min, features_df.columns.get_loc('is_local_min')] = 1
            
            # === 时间特征 ===
            # 提取时间相关特征
            features_df['hour'] = df.index.hour
            features_df['day_of_week'] = df.index.dayofweek
            features_df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
            
            # === 清理和验证 ===
            # 替换无穷大值和NaN
            features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            features_df.fillna(0, inplace=True)
            
            # 移除原始value列，只保留特征列
            feature_columns = [col for col in features_df.columns if col != 'value']
            features_df = features_df[feature_columns]
            
            self.logger.debug(
                "特征工程完成",
                original_features=1,
                extracted_features=len(feature_columns),
                feature_names=feature_columns[:5]  # 显示前5个特征名
            )
            
            return features_df
            
        except Exception as e:
            self.logger.error("特征工程失败", error=str(e))
            raise ValueError(f"特征工程失败: {str(e)}")
    
    
    # TODO: 添加其他检测算法方法
    # - _detect_isolation_forest
    # - _detect_z_score  
    # - _detect_statistical
    # - _generate_anomaly_points
    # - 其他辅助方法
    
    
# 导出类
__all__ = ["AIAnomalyDetector", "ModelMetadata", "AnomalyScoreLevel"]
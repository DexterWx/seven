from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Dict
import json

db = SQLAlchemy()

class IncomeHistory(TypeDecorator):
    """自定义收益历史记录类型"""
    impl = JSON
    
    def process_bind_param(self, value: List[Dict], dialect):
        """验证并处理输入数据"""
        if value is None:
            return []
            
        if not isinstance(value, list):
            raise ValueError("收益历史必须是列表类型")
            
        for item in value:
            if not isinstance(item, dict):
                raise ValueError("收益历史记录必须是字典类型")
            if "date" not in item or "amount" not in item:
                raise ValueError("收益历史记录必须包含 date 和 amount 字段")
            if not isinstance(item["amount"], (int, float)):
                raise ValueError("amount 必须是数字类型")
            try:
                datetime.strptime(item["date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("date 必须是 YYYY-MM-DD 格式")
        
        return value
    
    def process_result_value(self, value, dialect):
        """处理从数据库读取的数据"""
        if value is None:
            return []
        return value

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False, index=True)  # 手机号
    password = db.Column(db.String(128), nullable=False)  # 密码
    name = db.Column(db.String(50), index=True)  # 姓名
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # 创建时间
    last_login = db.Column(db.DateTime)  # 最后登录时间
    
    min_commission_rate = db.Column(db.Float, default=0)     # 最小分成比例
    max_commission_rate = db.Column(db.Float, default=0.2)   # 最大分成比例
    superior_name = db.Column(db.String(100))              # 上级名字
    superior_phone = db.Column(db.String(20), db.ForeignKey('users.phone'), nullable=True, index=True)  # 上级手机号
    unwithdrawn_amount = db.Column(db.Float, default=0)  # 未体现金额
    withdrawn_amount = db.Column(db.Float, default=0)    # 已提现金额
    applying_amount = db.Column(db.Float, default=0)    # 申请提现中的金额
    yesterday_income = db.Column(db.Float, default=0)    # 昨日收益
    month_income = db.Column(db.Float, default=0)        # 本月收益
    history_income = db.Column(db.JSON, default=list)    # 历史收益列表，格式为 [{"date": "2024-03-20", "amount": 1.23}, ...]
    team_yesterday_income = db.Column(db.Float, default=0)  # 团队昨日收益
    team_month_income = db.Column(db.Float, default=0)  # 团队本月收益
    team_history_sum = db.Column(db.Float, default=0)  # 团队历史收益总和
    team_history_income = db.Column(db.JSON, default=list)    # 团队历史收益列表，格式为 [{"date": "2024-03-20", "amount": 1.23}, ...]
    
    first_level_count = db.Column(db.Integer, default=0)   # 一级下线数量
    
    # 结算方式选择
    use_bank = db.Column(db.Boolean, default=True)  # True表示使用银行卡，False表示使用支付宝
    
    # 银行卡信息（可选字段）
    bank_card_number = db.Column(db.String(30), nullable=True)  # 银行卡号
    bank_holder_name = db.Column(db.String(50), nullable=True)  # 银行卡持卡人姓名
    bank_id_number = db.Column(db.String(20), nullable=True)    # 银行卡持卡人身份证号
    bank_phone = db.Column(db.String(11), nullable=True)        # 银行卡预留手机号
    
    # 支付宝信息（可选字段）
    alipay_account = db.Column(db.String(100), nullable=True)   # 支付宝账号
    alipay_holder_name = db.Column(db.String(50), nullable=True)  # 支付宝姓名
    alipay_id_number = db.Column(db.String(20), nullable=True)    # 支付宝身份证号
    alipay_phone = db.Column(db.String(11), nullable=True)        # 支付宝手机号
    
    # 添加设备关系
    devices = db.relationship('Device', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'min_commission_rate': self.min_commission_rate,
            'max_commission_rate': self.max_commission_rate,
            'superior_name': self.superior_name,
            'superior_phone': self.superior_phone,
            'unwithdrawn_amount': self.unwithdrawn_amount,
            'withdrawn_amount': self.withdrawn_amount,
            'applying_amount': self.applying_amount,
            'yesterday_income': self.yesterday_income,
            'month_income': self.month_income,
            'history_income': self.history_income,
            'team_yesterday_income': self.team_yesterday_income,
            'team_month_income': self.team_month_income,
            'team_history_sum': self.team_history_sum,
            'team_history_income': self.team_history_income,
            'first_level_count': self.first_level_count,
            'use_bank': self.use_bank,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            # 银行卡信息
            'bank_card_number': self.bank_card_number,
            'bank_holder_name': self.bank_holder_name,
            'bank_id_number': self.bank_id_number,
            'bank_phone': self.bank_phone,
            # 支付宝信息
            'alipay_account': self.alipay_account,
            'alipay_holder_name': self.alipay_holder_name,
            'alipay_id_number': self.alipay_id_number,
            'alipay_phone': self.alipay_phone
        }

class Device(db.Model):
    """设备模型"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)  # 改为自增ID
    device_id = db.Column(db.String(50), unique=True, index=True)  # 设备唯一标识
    phone = db.Column(db.String(20), db.ForeignKey('users.phone'), default='', index=True)  # 用户手机号
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 创建时间
    amount = db.Column(db.Float)                           # 设备金额
    is_returned = db.Column(db.Boolean, default=False)     # 是否返现
    is_paid = db.Column(db.Boolean, default=False)         # 是否打款
    remark = db.Column(db.Text)                            # 备注
    commission_rate = db.Column(db.Float, default=0.1)   # 分成比例 , 分给平台的
    first_commission_rate = db.Column(db.Float, default=0)     # 一级分成比例  分给上级的
    
    yesterday_income = db.Column(db.Float, default=0)    # 昨日收益
    income_history = db.Column(db.JSON, default=list)    # 历史收益列表，格式为 [{"date": "2024-03-20", "amount": 1.23}, ...]

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'amount': self.amount,
            'is_returned': self.is_returned,
            'is_paid': self.is_paid,
            'remark': self.remark,
            'commission_rate': self.commission_rate,
            'first_commission_rate': self.first_commission_rate,
            'yesterday_income': self.yesterday_income,
            'income_history': self.income_history
        }

class PlatformStats(db.Model):
    """平台统计数据"""
    __tablename__ = 'platform_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    withdrawn = db.Column(db.Float, default=0)  # 已提现金额
    unwithdrawn = db.Column(db.Float, default=0)  # 未提现金额
    total = db.Column(db.Float, default=0)  # 总金额
    commission_total = db.Column(db.Float, default=0)  # 抽成总额
    device_total = db.Column(db.Float, default=0)  # 设备总额
    return_total = db.Column(db.Float, default=0)  # 返现总额
    paid_return = db.Column(db.Float, default=0)  # 已打款返现
    unpaid_return = db.Column(db.Float, default=0)  # 未打款返现
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def to_dict(self):
        return {
            'id': self.id,
            'withdrawn': self.withdrawn,
            'unwithdrawn': self.unwithdrawn,
            'total': self.total,
            'commission_total': self.commission_total,
            'device_total': self.device_total,
            'return_total': self.return_total,
            'paid_return': self.paid_return,
            'unpaid_return': self.unpaid_return,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

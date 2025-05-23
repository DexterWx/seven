from models import db, User, Device, PlatformStats
from sqlalchemy import func, case

def calculate_withdrawn_amount():
    """计算已提现金额"""
    try:
        # 获取或创建平台统计记录
        stats = PlatformStats.query.first()
        if not stats:
            stats = PlatformStats()
            db.session.add(stats)

        # 计算已提现金额
        withdrawn_result = db.session.query(
            func.sum(User.withdrawn_amount).label('withdrawn')
        ).first()
        
        stats.withdrawn = withdrawn_result.withdrawn or 0
        stats.total = stats.withdrawn + stats.unwithdrawn

        # 保存更新
        db.session.commit()
        return stats.withdrawn
    except Exception as e:
        db.session.rollback()
        print(f"Error calculating withdrawn amount: {str(e)}")
        return None

def calculate_unwithdrawn_amount():
    """计算未提现金额"""
    try:
        # 获取或创建平台统计记录
        stats = PlatformStats.query.first()
        if not stats:
            stats = PlatformStats()
            db.session.add(stats)

        # 计算未提现金额
        unwithdrawn_result = db.session.query(
            func.sum(User.unwithdrawn_amount).label('unwithdrawn')
        ).first()
        
        stats.unwithdrawn = unwithdrawn_result.unwithdrawn or 0
        stats.total = stats.withdrawn + stats.unwithdrawn

        # 保存更新
        db.session.commit()
        return stats.unwithdrawn
    except Exception as e:
        db.session.rollback()
        print(f"Error calculating unwithdrawn amount: {str(e)}")
        return None

def get_withdrawn_amount():
    """获取已提现金额"""
    try:
        # 计算最新数据
        amount = calculate_withdrawn_amount()
        if amount is None:
            return None

        # 获取更新时间
        stats = PlatformStats.query.first()
        return {
            'amount': amount,
            'updated_at': stats.updated_at.isoformat() if stats.updated_at else None
        }
    except Exception as e:
        print(f"Error getting withdrawn amount: {str(e)}")
        return None

def get_unwithdrawn_amount():
    """获取未提现金额"""
    try:
        # 计算最新数据
        amount = calculate_unwithdrawn_amount()
        if amount is None:
            return None

        # 获取更新时间
        stats = PlatformStats.query.first()
        return {
            'amount': amount,
            'updated_at': stats.updated_at.isoformat() if stats.updated_at else None
        }
    except Exception as e:
        print(f"Error getting unwithdrawn amount: {str(e)}")
        return None

def get_commission_total():
    """获取抽成总额"""
    try:
        stats = PlatformStats.query.first()
        if not stats:
            return None
        return {
            'amount': stats.commission_total,
            'updated_at': stats.updated_at.isoformat() if stats.updated_at else None
        }
    except Exception as e:
        print(f"Error getting commission total: {str(e)}")
        return None

def get_device_total():
    """获取设备总额"""
    try:
        # 直接从设备表计算总额
        result = db.session.query(func.sum(Device.amount)).first()
        total = result[0] or 0
        
        # 更新平台统计数据
        stats = PlatformStats.query.first()
        if stats:
            stats.device_total = total
            db.session.commit()
            
        return {
            'amount': total,
            'updated_at': stats.updated_at.isoformat() if stats and stats.updated_at else None
        }
    except Exception as e:
        print(f"Error getting device total: {str(e)}")
        return None

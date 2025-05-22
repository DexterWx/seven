def update_user_income():
    """更新用户收益"""
    from models import db, User
    from agents.user import get_user_yesterday_income, get_user_month_income, get_team_yesterday_income, get_team_month_income
    
    try:
        users = User.query.all()
        for user in users:
            # 更新个人收益
            user.yesterday_income = get_user_yesterday_income(user.phone)
            user.month_income = get_user_month_income(user.phone)
            
            # 更新团队收益
            user.team_yesterday_income = get_team_yesterday_income(user.phone)
            user.team_month_income = get_team_month_income(user.phone)
            
        db.session.commit()
        print("用户收益更新成功")
    except Exception as e:
        db.session.rollback()
        print(f"更新用户收益失败: {str(e)}") 

"""
HR Analytics Dashboard - Comprehensive Data Analysis
Professional analytics for HR metrics and insights
"""

from sqlalchemy import create_engine, func, extract, case
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pandas as pd
import json

# Import ORM models (assuming they're in the same directory)
from orm import Base, Employee, Attendance, Event, Payroll, Review, KPIOverview

# Database connection
engine = create_engine('sqlite:///hr.sqlite', echo=False)
Session = sessionmaker(bind=engine)

class HRAnalytics:
    """Comprehensive HR Analytics Suite"""
    
    def __init__(self, session):
        self.session = session
    
    def analyze_workforce_composition(self):
        """
        Analyze workforce composition by department, role, and location
        """
        # By Department
        dept_distribution = self.session.query(
            Employee.dept,
            func.count(Employee.employee_id).label('headcount'),
            func.round(func.count(Employee.employee_id) * 100.0 / 
                      self.session.query(func.count(Employee.employee_id)).scalar(), 2).label('percentage')
        ).group_by(Employee.dept).order_by(func.count(Employee.employee_id).desc()).all()
        
        # By Role
        role_distribution = self.session.query(
            Employee.role,
            func.count(Employee.employee_id).label('headcount')
        ).group_by(Employee.role).order_by(func.count(Employee.employee_id).desc()).all()
        
        # By Location
        location_distribution = self.session.query(
            Employee.location,
            func.count(Employee.employee_id).label('headcount')
        ).group_by(Employee.location).order_by(func.count(Employee.employee_id).desc()).all()
        
        return {
            'by_department': [{'dept': d.dept, 'headcount': d.headcount, 'percentage': d.percentage} for d in dept_distribution],
            'by_role': [{'role': r.role, 'headcount': r.headcount} for r in role_distribution],
            'by_location': [{'location': l.location, 'headcount': l.headcount} for l in location_distribution]
        }
    
    def analyze_tenure_distribution(self):
        """
        Analyze employee tenure and retention patterns
        """
        employees = self.session.query(Employee).all()
        tenure_data = []
        
        for emp in employees:
            if emp.hire_date:
                tenure_days = (datetime.now() - emp.hire_date).days
                tenure_years = tenure_days / 365.25
                tenure_data.append({
                    'employee_id': emp.employee_id,
                    'name': f"{emp.first_name} {emp.last_name}",
                    'dept': emp.dept,
                    'tenure_years': round(tenure_years, 2)
                })
        
        df_tenure = pd.DataFrame(tenure_data)
        avg_tenure = df_tenure['tenure_years'].mean()
        median_tenure = df_tenure['tenure_years'].median()
        
        df_tenure['tenure_bracket'] = pd.cut(
            df_tenure['tenure_years'],
            bins=[0, 1, 3, 5, 10, 100],
            labels=['0-1 years', '1-3 years', '3-5 years', '5-10 years', '10+ years']
        )
        
        tenure_brackets = df_tenure['tenure_bracket'].value_counts().sort_index()
        dept_tenure = df_tenure.groupby('dept')['tenure_years'].mean().sort_values(ascending=False)
        
        return {
            'avg_tenure': round(avg_tenure, 2),
            'median_tenure': round(median_tenure, 2),
            'tenure_brackets': tenure_brackets.to_dict(),
            'dept_avg_tenure': dept_tenure.to_dict()
        }
    
    def analyze_attendance_patterns(self):
        """
        Analyze attendance patterns and absenteeism rates
        """
        total_records = self.session.query(func.count(Attendance.date)).scalar()
        total_absences = self.session.query(func.sum(Attendance.absent)).scalar()
        
        absence_rate = 0
        if total_records and total_absences:
            absence_rate = (total_absences / total_records) * 100
        
        employee_absences = self.session.query(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Employee.dept,
            func.count(Attendance.date).label('total_days'),
            func.sum(Attendance.absent).label('absent_days'),
            func.round(func.sum(Attendance.absent) * 100.0 / func.count(Attendance.date), 2).label('absence_rate')
        ).join(Attendance).group_by(Employee.employee_id).having(
            func.sum(Attendance.absent) > 0
        ).order_by(func.round(func.sum(Attendance.absent) * 100.0 / func.count(Attendance.date), 2).desc()).limit(10).all()
        
        dept_absences = self.session.query(
            Employee.dept,
            func.round(func.sum(Attendance.absent) * 100.0 / func.count(Attendance.date), 2).label('absence_rate')
        ).join(Attendance, Employee.employee_id == Attendance.employee_id).group_by(Employee.dept).order_by(
            func.round(func.sum(Attendance.absent) * 100.0 / func.count(Attendance.date), 2).desc()
        ).all()
        
        return {
            'overall_absence_rate': round(absence_rate, 2),
            'top_absentees': [{'name': f"{e.first_name} {e.last_name}", 'dept': e.dept, 'rate': e.absence_rate} for e in employee_absences],
            'dept_absence_rates': [{'dept': d.dept, 'rate': d.absence_rate} for d in dept_absences]
        }
    
    def analyze_payroll_compensation(self):
        """
        Analyze compensation structure and payroll distribution
        """
        salary_stats = self.session.query(
            func.min(Payroll.base_salary).label('min_salary'),
            func.max(Payroll.base_salary).label('max_salary'),
            func.avg(Payroll.base_salary).label('avg_salary'),
            func.sum(Payroll.base_salary).label('total_payroll')
        ).first()
        
        dept_compensation = self.session.query(
            Employee.dept,
            func.avg(Payroll.base_salary).label('avg_salary'),
            func.sum(Payroll.base_salary).label('total_cost')
        ).join(Payroll, Employee.employee_id == Payroll.employee_id).group_by(Employee.dept).order_by(func.avg(Payroll.base_salary).desc()).all()
        
        role_compensation = self.session.query(
            Employee.role,
            func.avg(Payroll.base_salary).label('avg_salary')
        ).join(Payroll, Employee.employee_id == Payroll.employee_id).group_by(Employee.role).order_by(func.avg(Payroll.base_salary).desc()).all()
        
        return {
            'overall': {
                'min': salary_stats.min_salary,
                'max': salary_stats.max_salary,
                'avg': round(salary_stats.avg_salary, 2),
                'total': salary_stats.total_payroll
            },
            'by_department': [{'dept': d.dept, 'avg': round(d.avg_salary, 2), 'total': d.total_cost} for d in dept_compensation],
            'by_role': [{'role': r.role, 'avg': round(r.avg_salary, 2)} for r in role_compensation]
        }
    
    def analyze_performance_reviews(self):
        """
        Analyze performance review scores and trends
        """
        perf_stats = self.session.query(
            func.avg(Review.score).label('avg_score')
        ).first()
        
        employee_performance = self.session.query(
            Employee.first_name,
            Employee.last_name,
            Employee.dept,
            func.avg(Review.score).label('avg_score')
        ).join(Review, Employee.employee_id == Review.employee_id).group_by(Employee.employee_id).order_by(func.avg(Review.score).desc()).all()
        
        dept_performance = self.session.query(
            Employee.dept,
            func.avg(Review.score).label('avg_score')
        ).join(Review, Employee.employee_id == Review.employee_id).group_by(Employee.dept).order_by(func.avg(Review.score).desc()).all()
        
        return {
            'overall_avg': round(perf_stats.avg_score, 2),
            'top_performers': [{'name': f"{e.first_name} {e.last_name}", 'dept': e.dept, 'score': round(e.avg_score, 2)} for e in employee_performance[:10]],
            'dept_performance': [{'dept': d.dept, 'avg_score': round(d.avg_score, 2)} for d in dept_performance]
        }
    
    def analyze_turnover_metrics(self):
        """
        Analyze employee turnover and retention
        """
        kpi = self.session.query(KPIOverview).first()
        
        turnover_rate = 0
        retention_rate = 0
        if kpi:
            turnover_rate = kpi.turnover_rate
            retention_rate = 1 - kpi.turnover_rate
        
        return {
            'headcount': kpi.headcount if kpi else 0,
            'terminations': kpi.terminations if kpi else 0,
            'turnover_rate': round(turnover_rate * 100, 2),
            'retention_rate': round(retention_rate * 100, 2)
        }
    
    def analyze_hiring_trends(self):
        """
        Analyze hiring patterns and trends
        """
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_hires = self.session.query(Employee).filter(Employee.hire_date >= six_months_ago).all()
        
        hiring_by_dept = {}
        for hire in recent_hires:
            hiring_by_dept[hire.dept] = hiring_by_dept.get(hire.dept, 0) + 1
            
        return {
            'recent_hires_count': len(recent_hires),
            'by_department': hiring_by_dept
        }

    def analyze_turnover_by_department(self):
        """
        Analyze employee turnover by department.
        """
        turnover_by_dept = self.session.query(
            Employee.dept,
            func.count(Event.employee_id).label('terminations')
        ).join(Event, Employee.employee_id == Event.employee_id).filter(Event.event_type == 'Termination').group_by(Employee.dept).all()
        
        return [{'dept': d.dept, 'terminations': d.terminations} for d in turnover_by_dept]

    def analyze_performance_vs_compensation(self):
        """
        Analyze the relationship between performance and compensation.
        """
        performance_compensation = self.session.query(
            Employee.first_name,
            Employee.last_name,
            Review.score,
            Payroll.base_salary
        ).join(Review, Employee.employee_id == Review.employee_id).join(Payroll, Employee.employee_id == Payroll.employee_id).all()
        
        return [{'name': f'{pc.first_name} {pc.last_name}', 'performance': pc.score, 'compensation': pc.base_salary} for pc in performance_compensation]

    def analyze_hiring_trends_by_role(self):
        """
        Analyze hiring patterns and trends by role.
        """
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_hires = self.session.query(Employee).filter(Employee.hire_date >= six_months_ago).all()
        
        hiring_by_role = {}
        for hire in recent_hires:
            hiring_by_role[hire.role] = hiring_by_role.get(hire.role, 0) + 1
            
        return hiring_by_role

    def run_all_analyses(self):
        return {
            'workforce_composition': self.analyze_workforce_composition(),
            'tenure_distribution': self.analyze_tenure_distribution(),
            'attendance_patterns': self.analyze_attendance_patterns(),
            'payroll_compensation': self.analyze_payroll_compensation(),
            'performance_reviews': self.analyze_performance_reviews(),
            'turnover_metrics': self.analyze_turnover_metrics(),
            'hiring_trends': self.analyze_hiring_trends(),
            'turnover_by_department': self.analyze_turnover_by_department(),
            'performance_vs_compensation': self.analyze_performance_vs_compensation(),
            'hiring_trends_by_role': self.analyze_hiring_trends_by_role()
        }

def get_analytics_summary():
    session = Session()
    try:
        analytics = HRAnalytics(session)
        summary = analytics.run_all_analyses()
        return summary
    finally:
        session.close()


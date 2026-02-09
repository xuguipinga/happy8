"""
定时任务调度器
使用 APScheduler 管理后台定时任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self, app=None):
        self.scheduler = None
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化调度器"""
        self.app = app
        
        # 检查是否启用自动更新
        if not app.config.get('AUTO_UPDATE_ENABLED', False):
            app.logger.info('自动更新功能已禁用')
            return
        
        # 创建后台调度器
        self.scheduler = BackgroundScheduler(
            daemon=True,
            timezone='Asia/Shanghai'
        )
        
        # 注册退出时关闭调度器
        atexit.register(lambda: self.shutdown())
        
        app.logger.info('定时任务调度器初始化完成')
    
    def start(self):
        """启动调度器"""
        if not self.scheduler:
            self.app.logger.warning('调度器未初始化,跳过启动')
            return
        
        if self.scheduler.running:
            self.app.logger.warning('调度器已在运行')
            return
        
        self.scheduler.start()
        self.app.logger.info('定时任务调度器已启动')
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            self.app.logger.info('定时任务调度器已关闭')
    
    def add_interval_job(self, func, minutes, job_id, **kwargs):
        """添加间隔触发任务"""
        if not self.scheduler:
            return
        
        trigger = IntervalTrigger(minutes=minutes)
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        self.app.logger.info(f'添加定时任务: {job_id} (间隔: {minutes}分钟)')
    
    def add_cron_job(self, func, cron_expr, job_id, **kwargs):
        """添加Cron表达式任务"""
        if not self.scheduler:
            return
        
        # 解析cron表达式
        parts = cron_expr.split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            self.app.logger.info(f'添加Cron任务: {job_id} ({cron_expr})')
    
    def remove_job(self, job_id):
        """移除任务"""
        if not self.scheduler:
            return
        
        try:
            self.scheduler.remove_job(job_id)
            self.app.logger.info(f'移除任务: {job_id}')
        except Exception as e:
            self.app.logger.error(f'移除任务失败: {e}')
    
    def get_jobs(self):
        """获取所有任务"""
        if not self.scheduler:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
            })
        return jobs


# 全局调度器实例
scheduler = TaskScheduler()

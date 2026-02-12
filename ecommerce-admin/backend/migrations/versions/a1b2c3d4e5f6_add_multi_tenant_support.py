"""add multi-tenant support

Revision ID: a1b2c3d4e5f6
Revises: 8b86a781c374
Create Date: 2026-02-12 01:58:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '8b86a781c374'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 创建租户表
    op.create_table('sys_tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False, comment='公司/店铺名称'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='租户代码'),
        sa.Column('contact_person', sa.String(length=100), nullable=True, comment='联系人'),
        sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='联系电话'),
        sa.Column('contact_email', sa.String(length=100), nullable=True, comment='联系邮箱'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否启用'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sys_tenants_code'), 'sys_tenants', ['code'], unique=True)
    
    # 2. 创建默认租户(用于现有数据)
    op.execute("""
        INSERT INTO sys_tenants (id, name, code, is_active, created_at) 
        VALUES (1, '默认租户', 'DEFAULT', 1, NOW())
    """)
    
    # 3. 为用户表添加租户字段
    op.add_column('sys_users', sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'))
    op.add_column('sys_users', sa.Column('role', sa.String(length=20), nullable=True, comment='角色: admin/user'))
    op.create_index(op.f('ix_sys_users_tenant_id'), 'sys_users', ['tenant_id'], unique=False)
    op.create_foreign_key('fk_sys_users_tenant_id', 'sys_users', 'sys_tenants', ['tenant_id'], ['id'])
    
    # 为现有用户分配默认租户并设置为admin
    op.execute("UPDATE sys_users SET tenant_id = 1, role = 'admin' WHERE tenant_id IS NULL")
    
    # 设置为NOT NULL
    op.alter_column('sys_users', 'tenant_id', nullable=False)
    
    # 4. 为订单表添加租户字段
    op.add_column('biz_orders', sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'))
    op.create_index(op.f('ix_biz_orders_tenant_id'), 'biz_orders', ['tenant_id'], unique=False)
    op.create_foreign_key('fk_biz_orders_tenant_id', 'biz_orders', 'sys_tenants', ['tenant_id'], ['id'])
    
    # 为现有订单分配默认租户
    op.execute("UPDATE biz_orders SET tenant_id = 1 WHERE tenant_id IS NULL")
    op.alter_column('biz_orders', 'tenant_id', nullable=False)
    
    # 5. 为产品表添加租户字段
    op.add_column('biz_products', sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'))
    op.create_index(op.f('ix_biz_products_tenant_id'), 'biz_products', ['tenant_id'], unique=False)
    op.create_foreign_key('fk_biz_products_tenant_id', 'biz_products', 'sys_tenants', ['tenant_id'], ['id'])
    
    # 为现有产品分配默认租户
    op.execute("UPDATE biz_products SET tenant_id = 1 WHERE tenant_id IS NULL")
    op.alter_column('biz_products', 'tenant_id', nullable=False)
    
    # 6. 为采购表添加租户字段
    op.add_column('biz_purchases', sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'))
    op.create_index(op.f('ix_biz_purchases_tenant_id'), 'biz_purchases', ['tenant_id'], unique=False)
    op.create_foreign_key('fk_biz_purchases_tenant_id', 'biz_purchases', 'sys_tenants', ['tenant_id'], ['id'])
    
    # 为现有采购分配默认租户
    op.execute("UPDATE biz_purchases SET tenant_id = 1 WHERE tenant_id IS NULL")
    op.alter_column('biz_purchases', 'tenant_id', nullable=False)
    
    # 7. 为物流表添加租户字段
    op.add_column('biz_logistics', sa.Column('tenant_id', sa.Integer(), nullable=True, comment='租户ID'))
    op.create_index(op.f('ix_biz_logistics_tenant_id'), 'biz_logistics', ['tenant_id'], unique=False)
    op.create_foreign_key('fk_biz_logistics_tenant_id', 'biz_logistics', 'sys_tenants', ['tenant_id'], ['id'])
    
    # 为现有物流分配默认租户
    op.execute("UPDATE biz_logistics SET tenant_id = 1 WHERE tenant_id IS NULL")
    op.alter_column('biz_logistics', 'tenant_id', nullable=False)


def downgrade():
    # 逆向操作 - 删除所有租户相关字段和表
    op.drop_constraint('fk_biz_logistics_tenant_id', 'biz_logistics', type_='foreignkey')
    op.drop_index(op.f('ix_biz_logistics_tenant_id'), table_name='biz_logistics')
    op.drop_column('biz_logistics', 'tenant_id')
    
    op.drop_constraint('fk_biz_purchases_tenant_id', 'biz_purchases', type_='foreignkey')
    op.drop_index(op.f('ix_biz_purchases_tenant_id'), table_name='biz_purchases')
    op.drop_column('biz_purchases', 'tenant_id')
    
    op.drop_constraint('fk_biz_products_tenant_id', 'biz_products', type_='foreignkey')
    op.drop_index(op.f('ix_biz_products_tenant_id'), table_name='biz_products')
    op.drop_column('biz_products', 'tenant_id')
    
    op.drop_constraint('fk_biz_orders_tenant_id', 'biz_orders', type_='foreignkey')
    op.drop_index(op.f('ix_biz_orders_tenant_id'), table_name='biz_orders')
    op.drop_column('biz_orders', 'tenant_id')
    
    op.drop_constraint('fk_sys_users_tenant_id', 'sys_users', type_='foreignkey')
    op.drop_index(op.f('ix_sys_users_tenant_id'), table_name='sys_users')
    op.drop_column('sys_users', 'role')
    op.drop_column('sys_users', 'tenant_id')
    
    op.drop_index(op.f('ix_sys_tenants_code'), table_name='sys_tenants')
    op.drop_table('sys_tenants')

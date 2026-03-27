-- --------------------------------------------------------
-- 电商后台管理系统 完整数据库表结构 (Final Verified Version)
-- --------------------------------------------------------

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for sys_tenants
-- ----------------------------
DROP TABLE IF EXISTS `sys_tenants`;
CREATE TABLE `sys_tenants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL COMMENT '公司/店铺名称',
  `code` varchar(50) NOT NULL COMMENT '租户代码',
  `contact_person` varchar(100) DEFAULT NULL COMMENT '联系人',
  `contact_phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `contact_email` varchar(100) DEFAULT NULL COMMENT '联系邮箱',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for sys_users
-- ----------------------------
DROP TABLE IF EXISTS `sys_users`;
CREATE TABLE `sys_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `parent_id` int DEFAULT NULL COMMENT '父账号ID',
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'user' COMMENT '角色: admin/user',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `sys_users_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_products
-- ----------------------------
DROP TABLE IF EXISTS `biz_products`;
CREATE TABLE `biz_products` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `sku` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `avg_cost_price` decimal(12,4) DEFAULT '0.0000',
  `latest_purchase_price` decimal(12,4) DEFAULT '0.0000',
  `landed_cost` decimal(12,4) DEFAULT '0.0000' COMMENT '落地成本(含运费)',
  `platform_fee_rate` decimal(5,4) DEFAULT '0.0000' COMMENT '平台费率',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `biz_products_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_inventory
-- ----------------------------
DROP TABLE IF EXISTS `biz_inventory`;
CREATE TABLE `biz_inventory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `model` varchar(100) NOT NULL COMMENT '型号 (如 B002)',
  `spec` varchar(100) DEFAULT NULL COMMENT '规格/尺寸 (如 20cm)',
  `series` varchar(50) DEFAULT NULL COMMENT '系列 (如 C系列)',
  `quantity` decimal(12,4) DEFAULT '0.0000' COMMENT '当前库存数量',
  `unit` varchar(20) DEFAULT 'pcs' COMMENT '单位',
  `avg_cost` decimal(12,4) DEFAULT '0.0000' COMMENT '平均入库成本',
  `image_url` varchar(255) DEFAULT NULL COMMENT '图片地址',
  `status` varchar(20) DEFAULT 'NORMAL' COMMENT '库存状态: NORMAL, LOW, EMPTY',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `idx_model` (`model`),
  KEY `idx_spec` (`spec`),
  KEY `idx_series` (`series`),
  CONSTRAINT `biz_inventory_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_orders
-- ----------------------------
DROP TABLE IF EXISTS `biz_orders`;
CREATE TABLE `biz_orders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `platform_order_no` varchar(100) NOT NULL COMMENT '平台订单号',
  `order_time` datetime DEFAULT NULL COMMENT '下单时间',
  `buyer_email` varchar(150) DEFAULT NULL COMMENT '买家邮箱',
  `company_name` varchar(150) DEFAULT NULL COMMENT '公司名称',
  `buyer_name` varchar(100) DEFAULT NULL COMMENT '买家姓名',
  `seller_name` varchar(100) DEFAULT NULL COMMENT '卖家账号',
  `product_name` varchar(255) DEFAULT NULL COMMENT '商品名称',
  `sku` varchar(255) DEFAULT NULL COMMENT 'SKU',
  `quantity` int DEFAULT NULL COMMENT '数量',
  `currency` varchar(10) DEFAULT NULL COMMENT '币种',
  `unit_price` decimal(12,4) DEFAULT NULL COMMENT '单价',
  `order_amount` decimal(12,4) DEFAULT NULL COMMENT '订单总额',
  `shipping_fee_income` decimal(12,4) DEFAULT NULL COMMENT '运费收入',
  `discount_amount` decimal(12,4) DEFAULT NULL COMMENT '折扣金额',
  `actual_paid` decimal(12,4) DEFAULT '0.0000' COMMENT '实付金额',
  `order_status` varchar(50) DEFAULT NULL COMMENT '状态',
  `order_type` varchar(50) DEFAULT NULL COMMENT '订单类型',
  `has_attachment` tinyint(1) DEFAULT NULL COMMENT '是否有合同',
  `actual_delivery_time` datetime DEFAULT NULL COMMENT '实际发货时间',
  `buyer_country` varchar(50) DEFAULT NULL COMMENT '买家国家',
  `tax_fee` decimal(12,4) DEFAULT NULL COMMENT '税费',
  `shipping_address` text COMMENT '收货地址',
  `remark` text COMMENT '备注',
  `initial_payment` decimal(12,4) DEFAULT NULL COMMENT '预付款',
  `balance_payment` decimal(12,4) DEFAULT NULL COMMENT '尾款',
  `appointed_delivery_time` datetime DEFAULT NULL COMMENT '约定发货时间',
  `cost_price` decimal(12,4) DEFAULT '0.0000' COMMENT '采购成本',
  `logistics_cost` decimal(12,4) DEFAULT '0.0000' COMMENT '物流支出',
  `profit` decimal(12,4) DEFAULT NULL COMMENT '毛利',
  `profit_rate` decimal(10,4) DEFAULT '0.0000' COMMENT '利润率',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `platform_order_no` (`platform_order_no`),
  KEY `tenant_id` (`tenant_id`),
  KEY `idx_sku` (`sku`),
  CONSTRAINT `biz_orders_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_purchases
-- ----------------------------
DROP TABLE IF EXISTS `biz_purchases`;
CREATE TABLE `biz_purchases` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `purchase_no` varchar(100) NOT NULL COMMENT '采购单号',
  `supplier_company` varchar(150) DEFAULT NULL COMMENT '供应商公司',
  `supplier_member` varchar(100) DEFAULT NULL COMMENT '供应商对接人',
  `buyer_company` varchar(150) DEFAULT NULL COMMENT '采购方公司',
  `buyer_member` varchar(100) DEFAULT NULL COMMENT '采购员',
  `sku` varchar(255) DEFAULT NULL COMMENT 'SKU',
  `quantity` decimal(12,4) DEFAULT NULL COMMENT '采购总数量',
  `goods_amount` decimal(12,4) DEFAULT NULL COMMENT '货品总价',
  `shipping_fee` decimal(12,4) DEFAULT NULL COMMENT '总运费',
  `discount` decimal(12,4) DEFAULT NULL COMMENT '总折扣',
  `actual_payment` decimal(12,4) DEFAULT NULL COMMENT '实付款',
  `order_status` varchar(50) DEFAULT NULL COMMENT '采购状态',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `pay_time` datetime DEFAULT NULL COMMENT '付款时间',
  `logistics_company` varchar(100) DEFAULT NULL COMMENT '物流公司',
  `logistics_no` varchar(100) DEFAULT NULL COMMENT '物流单号',
  `receiver_address` text COMMENT '收货地址',
  `receiver_name` varchar(100) DEFAULT NULL COMMENT '收货人姓名',
  `receiver_phone` varchar(50) DEFAULT NULL COMMENT '联系电话',
  `receiver_mobile` varchar(50) DEFAULT NULL COMMENT '联系手机',
  `unit` varchar(20) DEFAULT NULL COMMENT '单位',
  `buyer_note` text COMMENT '买家留言',
  `invoice_title` varchar(200) DEFAULT NULL COMMENT '发票抬头',
  `tax_id` varchar(100) DEFAULT NULL COMMENT '纳税人识别号',
  `invoice_address_phone` varchar(255) DEFAULT NULL COMMENT '发票地址电话',
  `invoice_bank_account` varchar(255) DEFAULT NULL COMMENT '发票开户行及账号',
  `invoice_receiver_address` text COMMENT '发票收票地址',
  `is_dropship` tinyint(1) DEFAULT NULL COMMENT '是否代发',
  `upstream_order_no` varchar(100) DEFAULT NULL COMMENT '下游订单号',
  `order_batch_no` varchar(100) DEFAULT NULL COMMENT '下单批次号',
  `shipper_name` varchar(100) DEFAULT NULL COMMENT '发货方',
  `zip_code` varchar(20) DEFAULT NULL COMMENT '邮编',
  `category` varchar(100) DEFAULT NULL COMMENT '货品种类',
  `agent_name` varchar(100) DEFAULT NULL COMMENT '代理商姓名',
  `agent_contact` varchar(100) DEFAULT NULL COMMENT '代理商联系方式',
  `dropship_provider_id` varchar(100) DEFAULT NULL COMMENT '代发服务商id',
  `micro_order_no` varchar(100) DEFAULT NULL COMMENT '微商订单号',
  `downstream_channel` varchar(100) DEFAULT NULL COMMENT '下游渠道',
  `order_company_entity` varchar(100) DEFAULT NULL COMMENT '下单公司主体',
  `initiator_login_name` varchar(100) DEFAULT NULL COMMENT '发起人登录名',
  `is_auto_pay` varchar(100) DEFAULT NULL COMMENT '是否发起免密支付',
  PRIMARY KEY (`id`),
  UNIQUE KEY `purchase_no` (`purchase_no`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `biz_purchases_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_purchase_items
-- ----------------------------
DROP TABLE IF EXISTS `biz_purchase_items`;
CREATE TABLE `biz_purchase_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `purchase_id` bigint NOT NULL COMMENT '采购主表ID',
  `sku` varchar(255) NOT NULL COMMENT 'SKU',
  `product_name` varchar(255) DEFAULT NULL COMMENT '货品标题',
  `model` varchar(100) DEFAULT NULL COMMENT '型号',
  `material_no` varchar(100) DEFAULT NULL COMMENT '物料编号',
  `product_no` varchar(100) DEFAULT NULL COMMENT '货号',
  `offer_id` varchar(100) DEFAULT NULL COMMENT 'Offer ID',
  `quantity` decimal(12,4) NOT NULL COMMENT '采购数量',
  `unit_price` decimal(12,4) DEFAULT NULL COMMENT '采购单价',
  `goods_amount` decimal(12,4) DEFAULT NULL COMMENT '单项总价',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `purchase_id` (`purchase_id`),
  KEY `idx_sku` (`sku`),
  CONSTRAINT `biz_purchase_items_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`),
  CONSTRAINT `biz_purchase_items_ibfk_2` FOREIGN KEY (`purchase_id`) REFERENCES `biz_purchases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_order_purchase_links
-- ----------------------------
DROP TABLE IF EXISTS `biz_order_purchase_links`;
CREATE TABLE `biz_order_purchase_links` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `order_id` bigint NOT NULL,
  `purchase_id` bigint NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `order_id` (`order_id`),
  KEY `purchase_id` (`purchase_id`),
  CONSTRAINT `biz_order_purchase_links_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`),
  CONSTRAINT `biz_order_purchase_links_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `biz_orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `biz_order_purchase_links_ibfk_3` FOREIGN KEY (`purchase_id`) REFERENCES `biz_purchases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_logistics
-- ----------------------------
DROP TABLE IF EXISTS `biz_logistics`;
CREATE TABLE `biz_logistics` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL COMMENT '租户ID',
  `tracking_no` varchar(100) NOT NULL COMMENT '运单号',
  `ref_no` varchar(100) DEFAULT NULL COMMENT '参考号/订单号',
  `logistics_channel` varchar(100) DEFAULT NULL COMMENT '物流渠道',
  `order_status` varchar(50) DEFAULT NULL COMMENT '订单状态',
  `sent_date` date DEFAULT NULL COMMENT '发货日期',
  `destination` varchar(50) DEFAULT NULL COMMENT '目的地',
  `zone` varchar(20) DEFAULT NULL COMMENT '分区',
  `pre_weight` decimal(10,3) DEFAULT NULL COMMENT '预报重量',
  `actual_weight` decimal(10,3) DEFAULT NULL COMMENT '实际重量',
  `declared_value` decimal(12,4) DEFAULT NULL COMMENT '申报价值',
  `shipping_fee` decimal(12,4) DEFAULT NULL COMMENT '运费',
  `discount_fee` decimal(12,4) DEFAULT NULL COMMENT '优惠金额',
  `actual_fee` decimal(12,4) DEFAULT NULL COMMENT '实收运费',
  `payment_method` varchar(50) DEFAULT NULL COMMENT '支付方式',
  `service_type` varchar(100) DEFAULT NULL COMMENT '服务类型',
  `warehouse` varchar(100) DEFAULT NULL COMMENT '仓库',
  `inbound_time` datetime DEFAULT NULL COMMENT '入库时间',
  `outbound_time` datetime DEFAULT NULL COMMENT '出库时间',
  `payment_time` datetime DEFAULT NULL COMMENT '支付时间',
  `customer_order_no` varchar(100) DEFAULT NULL COMMENT '客户订单号',
  `sender_name` varchar(100) DEFAULT NULL COMMENT '发件人姓名',
  `sender_email` varchar(150) DEFAULT NULL COMMENT '发件人邮件',
  `ordering_account` varchar(100) DEFAULT NULL COMMENT '下单账号',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `tracking_no` (`tracking_no`),
  KEY `tenant_id` (`tenant_id`),
  KEY `idx_ref_no` (`ref_no`),
  CONSTRAINT `biz_logistics_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_stock_records
-- ----------------------------
DROP TABLE IF EXISTS `biz_stock_records`;
CREATE TABLE `biz_stock_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `inventory_id` bigint NOT NULL,
  `order_id` bigint DEFAULT NULL COMMENT '关联订单ID (出库)',
  `purchase_id` bigint DEFAULT NULL COMMENT '关联采购单ID (入库)',
  `record_type` varchar(20) NOT NULL COMMENT '类型: IN(入库), OUT(出库), ADJ(调整/报损)',
  `change_quantity` decimal(12,4) NOT NULL COMMENT '变动数量',
  `balance_quantity` decimal(12,4) DEFAULT NULL COMMENT '变动后余量',
  `unit_cost` decimal(12,4) DEFAULT NULL COMMENT '本次变动的单价成本',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注 (如: 报损、样品领取)',
  `operator_name` varchar(50) DEFAULT NULL COMMENT '操作人姓名',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `inventory_id` (`inventory_id`),
  KEY `order_id` (`order_id`),
  KEY `purchase_id` (`purchase_id`),
  CONSTRAINT `biz_stock_records_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`),
  CONSTRAINT `biz_stock_records_ibfk_2` FOREIGN KEY (`inventory_id`) REFERENCES `biz_inventory` (`id`),
  CONSTRAINT `biz_stock_records_ibfk_3` FOREIGN KEY (`order_id`) REFERENCES `biz_orders` (`id`),
  CONSTRAINT `biz_stock_records_ibfk_4` FOREIGN KEY (`purchase_id`) REFERENCES `biz_purchases` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for alembic_version (Keep flask-migrate happy)
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `alembic_version` VALUES ('8b86a781c374');

-- ----------------------------
-- Initial Data
-- ----------------------------
INSERT INTO `sys_tenants` (`name`, `code`, `is_active`) VALUES ('默认租户', 'DEFAULT', 1);

SET FOREIGN_KEY_CHECKS = 1;

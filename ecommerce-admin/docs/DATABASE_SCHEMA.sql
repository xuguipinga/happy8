-- --------------------------------------------------------
-- 电商后台管理系统 完整数据库表结构 (Manual Setup)
-- --------------------------------------------------------

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for sys_tenants
-- ----------------------------
DROP TABLE IF EXISTS `sys_tenants`;
CREATE TABLE `sys_tenants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for sys_users
-- ----------------------------
DROP TABLE IF EXISTS `sys_users`;
CREATE TABLE `sys_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password_hash` varchar(128) NOT NULL,
  `role` varchar(20) DEFAULT 'staff',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `sys_users_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_inventory
-- ----------------------------
DROP TABLE IF EXISTS `biz_inventory`;
CREATE TABLE `biz_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `model` varchar(100) NOT NULL,
  `name` varchar(200) NOT NULL,
  `status` varchar(20) DEFAULT 'active',
  `sku` varchar(255) DEFAULT NULL,
  `sku_quantity` varchar(50) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT '0.00',
  `cost_price` decimal(10,2) DEFAULT '0.00',
  `total_stock` int DEFAULT '0',
  `notes` text,
  `image_url` varchar(500) DEFAULT NULL,
  `series` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `idx_series` (`series`),
  CONSTRAINT `biz_inventory_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_orders
-- ----------------------------
DROP TABLE IF EXISTS `biz_orders`;
CREATE TABLE `biz_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `order_no` varchar(64) NOT NULL,
  `platform` varchar(50) DEFAULT NULL,
  `store_name` varchar(100) DEFAULT NULL,
  `total_price` decimal(10,2) DEFAULT '0.00',
  `status` varchar(20) DEFAULT 'pending',
  `remark` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_no` (`order_no`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `biz_orders_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_purchase_orders
-- ----------------------------
DROP TABLE IF EXISTS `biz_purchase_orders`;
CREATE TABLE `biz_purchase_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tenant_id` int NOT NULL,
  `purchase_no` varchar(64) NOT NULL,
  `supplier` varchar(100) DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT '0.00',
  `status` varchar(20) DEFAULT 'pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `purchase_no` (`purchase_no`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `biz_purchase_orders_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `sys_tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_order_purchase_links
-- ----------------------------
DROP TABLE IF EXISTS `biz_order_purchase_links`;
CREATE TABLE `biz_order_purchase_links` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `purchase_order_id` int NOT NULL,
  `sku` varchar(255) DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `purchase_order_id` (`purchase_order_id`),
  CONSTRAINT `biz_order_purchase_links_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `biz_orders` (`id`),
  CONSTRAINT `biz_order_purchase_links_ibfk_2` FOREIGN KEY (`purchase_order_id`) REFERENCES `biz_purchase_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_purchase_items
-- ----------------------------
DROP TABLE IF EXISTS `biz_purchase_items`;
CREATE TABLE `biz_purchase_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `purchase_order_id` int NOT NULL,
  `inventory_id` int NOT NULL,
  `quantity` int DEFAULT '1',
  `unit_price` decimal(10,2) DEFAULT '0.00',
  `total_price` decimal(10,2) DEFAULT '0.00',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `purchase_order_id` (`purchase_order_id`),
  KEY `inventory_id` (`inventory_id`),
  CONSTRAINT `biz_purchase_items_ibfk_1` FOREIGN KEY (`purchase_order_id`) REFERENCES `biz_purchase_orders` (`id`),
  CONSTRAINT `biz_purchase_items_ibfk_2` FOREIGN KEY (`inventory_id`) REFERENCES `biz_inventory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_logistics_info
-- ----------------------------
DROP TABLE IF EXISTS `biz_logistics_info`;
CREATE TABLE `biz_logistics_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `carrier` varchar(100) DEFAULT NULL,
  `tracking_no` varchar(100) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'shipped',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `biz_logistics_info_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `biz_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for biz_logistics_updates
-- ----------------------------
DROP TABLE IF EXISTS `biz_logistics_updates`;
CREATE TABLE `biz_logistics_updates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `logistics_id` int NOT NULL,
  `description` text,
  `status_time` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `logistics_id` (`logistics_id`),
  CONSTRAINT `biz_logistics_updates_ibfk_1` FOREIGN KEY (`logistics_id`) REFERENCES `biz_logistics_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Initial Data
-- ----------------------------
INSERT INTO `sys_tenants` (`name`, `code`, `is_active`) VALUES ('默认租户', 'DEFAULT', 1);

SET FOREIGN_KEY_CHECKS = 1;

/*
 Navicat PostgreSQL Data Transfer

 Source Server         : RCStock Live Database
 Source Server Type    : PostgreSQL
 Source Server Version : 130007 (130007)
 Source Host           : rcstock.clpa39luybqh.eu-central-1.rds.amazonaws.com:5432
 Source Catalog        : rcstock
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 130007 (130007)
 File Encoding         : 65001

 Date: 05/10/2022 19:16:25
*/


-- ----------------------------
-- Table structure for tbl_products
-- ----------------------------
DROP TABLE IF EXISTS "public"."tbl_products";
CREATE TABLE "public"."tbl_products" (
  "photo" text COLLATE "pg_catalog"."default",
  "manufacturer" varchar(255) COLLATE "pg_catalog"."default",
  "product_name" varchar(1024) COLLATE "pg_catalog"."default",
  "price" varchar(10) COLLATE "pg_catalog"."default",
  "link" text COLLATE "pg_catalog"."default",
  "shop_id" int2,
  "stock_status" varchar(255) COLLATE "pg_catalog"."default",
  "sku" varchar(255) COLLATE "pg_catalog"."default",
  "date_search" date,
  "id" int4 NOT NULL DEFAULT nextval('tbl_products_id_seq'::regclass),
  "email" varchar(255) COLLATE "pg_catalog"."default"
)
;

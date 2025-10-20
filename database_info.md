服务器root密码：Svolt@2020.cn
User：datacenter; Password: Svolt.ai%36
User: ana; Password: Svoltana36

database_name: dqdb
shema: dws
table_name: dws_domestic_vehicle_sales_data_by_week;

DROP TABLE IF EXISTS dws.dws_domestic_vehicle_sales_data_by_week;
CREATE TABLE dws.dws_domestic_vehicle_sales_data_by_week (
    enterprise_short_name varchar(100),
    use_type varchar(50),
    car_brand varchar(50),
    model varchar(50),
    model_specification varchar(500),
    vehicle_class varchar(50),
    vehicle_class_autohome varchar(50),
    overall_length integer,
    year_code varchar(4),
    week varchar(10),
    week_code varchar(20),
    energy_type varchar(50),
    fuel_type varchar(50),
    vehicle_type varchar(50),
    wheelbase integer,
    quantity integer,
    insert_time TIMESTAMP
);

COMMENT ON TABLE dws.dws_domestic_vehicle_sales_data_by_week IS '国内乘用车周度上险数据';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.enterprise_short_name IS '企业简称';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.use_type IS '使用性质';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.car_brand IS '品牌';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.model IS '车型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.model_specification IS '细化车型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.vehicle_class IS '车型级别';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.vehicle_class_autohome IS '细化车型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.overall_length IS '外廊长';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.year_code IS '上险年份';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.week IS '上险周数';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.week_code IS '上险年周';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.energy_type IS '能源类型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.fuel_type IS '燃料类型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.vehicle_type IS '车型类别';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.wheelbase IS '轴距。单位CM';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.quantity IS '销售数量';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.insert_time IS '插入时间';
COMMENT ON TABLE dws.dws_domestic_vehicle_sales_data_by_week IS '国内乘用车周度上险数据';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.enterprise_short_name IS '企业简称';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.use_type IS '使用性质';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.car_brand IS '品牌';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.model IS '车型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.model_specification IS '细化车型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.vehicle_class IS '车型级别';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.vehicle_class_autohome IS '细化车型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.overall_length IS '外廊长';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.year_code IS '上险年份';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.week IS '上险周数';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.week_code IS '上险年周';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.energy_type IS '能源类型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.fuel_type IS '燃料类型';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.vehicle_type IS '车型类别';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.wheelbase IS '轴距。单位CM';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.quantity IS '销售数量';
COMMENT ON COLUMN dws.dws_domestic_vehicle_sales_data_by_week.insert_time IS '插入时间';



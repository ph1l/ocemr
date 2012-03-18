ALTER TABLE ocemr_labtype add column `cost` double precision NOT NULL default 0;
ALTER TABLE ocemr_medtype add column `cost` double precision NOT NULL default 0;
ALTER TABLE ocemr_labtype add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_medtype add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_diagnosistype add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_patient add column `altContactName` varchar(32) NOT NULL
         default "";
ALTER TABLE ocemr_patient add column `altContactPhone` varchar(32) NOT NULL
         default "";
INSERT INTO ocemr_vitaltype VALUES('','SpO2','%',0.0,100.0);
INSERT INTO ocemr_vitaltype VALUES('','Oxygen','%',0.0,100.0);

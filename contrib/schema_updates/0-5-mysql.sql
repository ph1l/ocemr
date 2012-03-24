ALTER TABLE ocemr_labtype add column `cost` double precision NOT NULL default 0;
ALTER TABLE ocemr_medtype add column `cost` double precision NOT NULL default 0;
ALTER TABLE ocemr_labtype add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_medtype add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_diagnosistype add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_village add column `active` bool NOT NULL default 1;
ALTER TABLE ocemr_patient add column `altContactName` varchar(32) NOT NULL
         default "";
ALTER TABLE ocemr_patient add column `altContactPhone` varchar(32) NOT NULL
         default "";

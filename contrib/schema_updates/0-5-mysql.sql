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
INSERT INTO ocemr_vactype VALUES('','BCG',1);
INSERT INTO ocemr_vactype VALUES('','Polio 0',1);
INSERT INTO ocemr_vactype VALUES('','Polio 1',1);
INSERT INTO ocemr_vactype VALUES('','DPT -HepB+Hib 1',1);
INSERT INTO ocemr_vactype VALUES('','PCV 1',1);
INSERT INTO ocemr_vactype VALUES('','Rota 1',1);
INSERT INTO ocemr_vactype VALUES('','Polio 2',1);
INSERT INTO ocemr_vactype VALUES('','DPT -HepB+Hib 2',1);
INSERT INTO ocemr_vactype VALUES('','PCV 2',1);
INSERT INTO ocemr_vactype VALUES('','Rota 2',1);
INSERT INTO ocemr_vactype VALUES('','Polio 3',1);
INSERT INTO ocemr_vactype VALUES('','DPT -HepB+Hib 3',1);
INSERT INTO ocemr_vactype VALUES('','PCV 3',1);
INSERT INTO ocemr_vactype VALUES('','Rota 3',1);
INSERT INTO ocemr_vactype VALUES('','Measles',1);


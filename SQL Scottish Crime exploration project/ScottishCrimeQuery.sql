/* 
Exploration of Scottish Crime Date (1996-2022)
https://statistics.gov.scot/resource?uri=http%3A%2F%2Fstatistics.gov.scot%2Fdata%2Frecorded-crime

Skills used: 
Temp tables, CTEs, Joins, Aggregate Functons, Windows Functions, Subqueries

*/

Select FeatureName, DateCode, [Value], CrimeOrOffence
From PortfolioProject.dbo.ScottishCrime;

-- Select data with FeatureName -> Scotland
Select FeatureName, DateCode, [Value], CrimeOrOffence
From PortfolioProject.dbo.ScottishCrime
Where FeatureName Like '%Scotland%'
Order By DateCode, CrimeOrOffence;

-- Use CTEs and join to create RecordedVale & RateValue columns

-- Create temporary table
Create Table #ScottishCrimeJoined (
FeatureName CHAR(100),
DateCode VARCHAR(9),
RecordedValue int,
RateValue int,
CrimeOrOffence CHAR(100));

-- Create two CTEs RecordedVale and RateValue
with RecordedValue as
(Select FeatureName, DateCode, [Value] as RecordedValue, CrimeOrOffence
From PortfolioProject.dbo.ScottishCrime
Where Units Like '%Recorded%'),

RateValue as
(Select FeatureName, DateCode, [Value] as RateValue, CrimeOrOffence
From PortfolioProject.dbo.ScottishCrime
Where Units Like '%Rate%' )

-- Inner join RecordedValue & RateValue
Insert Into #ScottishCrimeJoined
Select t1.FeatureName, t1.DateCode, t1.RecordedValue, t2.RateValue, 
t1.CrimeOrOffence
From RecordedValue as t1
JOIN ( Select FeatureName, DateCode, RateValue, CrimeOrOffence
	From RateValue) as t2
on t1.FeatureName = t2.FeatureName And 
t1.DateCode = t2.DateCode And t1.CrimeOrOffence = t2.CrimeOrOffence;

Select *
From #ScottishCrimeJoined;

-- Calculate the population from the rate & count values.
-- Pop. estimate = (value count/ value rate) * 10,000

Create Table #ScottishCrimePop (
FeatureName CHAR(100),
DateCode VARCHAR(9),
PopulationEstimate int,
RecordedValue int,
RateValue int,
CrimeOrOffence CHAR(100));

-- Partition by to average population estimate 
-- making it consistant over the same DateCode and FeatureName
Insert #ScottishCrimePop
Select FeatureName, DateCode, AVG((cast(RecordedValue as float)/NULLIF(cast(RateValue as float),0))*10000) 
Over (Partition By DateCode, FeatureName) as PopulationEstimate,
RecordedValue, RateValue, CrimeOrOffence
From #ScottishCrimeJoined;

Drop Table #ScottishCrimeJoined;

Select *
From #ScottishCrimePop
order by FeatureName, DateCode;

---- Do population estimates make sense?
--Select SUM(PopulationEstimate) as CurrentPopulation
--From #ScottishCrimePop
--Where FeatureName != 'Scotland' And DateCode = '2021/2022'
--And CrimeOrOffence Like '%Vandalism%'; --Yes

-- Overall RateValue by FeatureName using a From subquery

Select DISTINCT(FeatureName), Round(AVG(Rate),0) as AverageRate
From (Select FeatureName, DateCode, PopulationEstimate,
	cast(SUM(RecordedValue) as float)/cast(PopulationEstimate as float)*10000 as Rate 
	From #ScottishCrimePop
	Where CrimeOrOffence != 'All%' And FeatureName != 'Scotland'
	Group By FeatureName, DateCode, PopulationEstimate
	) as RateByFeature
Group By FeatureName
Order By AverageRate DESC;

-- Overall RateValue by DateCode using a From subquery

Select DISTINCT(DateCode), Round(AVG(Rate),0) as AverageRate
From (Select FeatureName, DateCode, PopulationEstimate,
	cast(SUM(RecordedValue) as float)/cast(PopulationEstimate as float)*10000 as Rate 
	From #ScottishCrimePop
	Where CrimeOrOffence != 'All%' And FeatureName != 'Scotland'
	Group By FeatureName, DateCode, PopulationEstimate
	) as RateByYear
Group By DateCode
Order By AverageRate DESC;

-- Overall RateValue by Crime/offence using a From subquery

Select DISTINCT(CrimeOrOffence), Round(AVG(Rate),2) as AverageRate
From (Select CrimeOrOffence, DateCode, PopulationEstimate,
	cast(SUM(RecordedValue) as float)/cast(PopulationEstimate as float)*10000 as Rate 
	From #ScottishCrimePop
	Where CrimeOrOffence != 'All%' And FeatureName != 'Scotland'
	Group By CrimeOrOffence, DateCode, PopulationEstimate
	) as RateByCrime
Group By CrimeOrOffence
Order By CrimeOrOffence DESC;

---- Check AverageRate against Rate for different years
--Select CrimeOrOffence, RateValue
--From #ScottishCrimePop
--Where DateCode = '2013/2014' and FeatureName = 'Scotland'
--order by CrimeOrOffence DESC; --> There is good general agreement.

--Retrieve data from Scottish council tax table

Select *
From PortfolioProject.dbo.ScottishCouncilTax

--Use join to create uncollected, billed, collected, & CollectionRate columns

Create Table #ScottishCouncilTaxRate (
FeatureName CHAR(100),
DateCode VARCHAR(9),
Uncollected float,
Billed float,
Collected float,
CollectionRate float);

Insert #ScottishCouncilTaxRate
Select t1.FeatureName, t1.DateCode, t1.[Value] as Uncollected, t2.Billed,
t3.Collected, t4.CollectionRate
From (
	Select *
	From PortfolioProject.dbo.ScottishCouncilTax
	Where CouncilTaxCollection = 'Uncollected'
	) as t1
Join(
	Select FeatureName, DateCode, [Value] as Billed
	From PortfolioProject.dbo.ScottishCouncilTax
	Where CouncilTaxCollection = 'Billed') as t2
On t1.FeatureName = t2.FeatureName And t1.DateCode = t2.DateCode
Join(
	Select FeatureName, DateCode, [Value] as Collected
	From PortfolioProject.dbo.ScottishCouncilTax
	Where CouncilTaxCollection = 'Collected') as t3
On t1.FeatureName = t3.FeatureName And t1.DateCode = t3.DateCode
Join(
	Select FeatureName, DateCode, [Value] as CollectionRate
	From PortfolioProject.dbo.ScottishCouncilTax
	Where CouncilTaxCollection = 'Collection Rate') as t4
On t1.FeatureName = t4.FeatureName And t1.DateCode = t4.DateCode;

--Note unit of Uncollected, billed and collected are million £

Select *
From #ScottishCouncilTaxRate
Where FeatureName = 'City of Edinburgh'
order by DateCode DESC;

--Get tax data for each county in 2021/2022
--Get average Crime Rate / county 2021/2022

Select Tax.FeatureName, Tax.Collected, Crime.AverageRate, Crime.PopulationEstimate,
Round((AverageRate/10000)*PopulationEstimate,0) as EstimatedRecordedValue
From ( 
	Select *
	From #ScottishCouncilTaxRate
	Where DateCode = '2021/2022' And FeatureName != 'Scotland'
	) as Tax
Join(
Select DISTINCT(FeatureName), Round(AVG(Rate),0) as AverageRate, PopulationEstimate
From (Select FeatureName, PopulationEstimate,
	cast(SUM(RecordedValue) as float)/cast(PopulationEstimate as float)*10000 as Rate 
	From #ScottishCrimePop
	Where DateCode = '2021/2022' And FeatureName != 'Scotland' And CrimeOrOffence Not Like '%All%'
	Group By FeatureName, PopulationEstimate
	) as RateByCrime
Group By FeatureName, PopulationEstimate) as Crime
On Tax.FeatureName = Crime.FeatureName
Order By EstimatedRecordedValue DESC;

---- Does EstimatedRecordedValue agree with SUM(RecordedValue) ?
--Select FeatureName, Sum(RecordedValue) As RecordedValue
--From #ScottishCrimePop
--Where FeatureName = 'City of Edinburgh' And DateCode = '2021/2022' 
--And (CrimeOrOffence Like '%All Crime%' OR CrimeOrOffence Like '%All Offence%')
--Group By FeatureName; --Yes
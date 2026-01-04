FraudSummary = 
let
    Source = Csv.Document(File.Contents("d:\Projects\Privacy-Safe Cross-Company Data Insights\powerbi\fraud_summary.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

InclusionSummary = 
let
    Source = Csv.Document(File.Contents("d:\Projects\Privacy-Safe Cross-Company Data Insights\powerbi\inclusion_summary.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

TradingSummary = 
let
    Source = Csv.Document(File.Contents("d:\Projects\Privacy-Safe Cross-Company Data Insights\powerbi\trading_summary.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

BankCustomers = 
let
    Source = Csv.Document(File.Contents("d:\Projects\Privacy-Safe Cross-Company Data Insights\powerbi\bank_customers.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

InsurerCustomers = 
let
    Source = Csv.Document(File.Contents("d:\Projects\Privacy-Safe Cross-Company Data Insights\powerbi\insurer_customers.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

BrokerageCustomers = 
let
    Source = Csv.Document(File.Contents("d:\Projects\Privacy-Safe Cross-Company Data Insights\powerbi\brokerage_customers.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

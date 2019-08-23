#!/bin/bash
curl -X GET "https://reciter.weill.cornell.edu/reciter/feature-generator/by/uid?uid=paa2013&totalStandardizedArticleScore=1&useGoldStandard=AS_EVIDENCE&analysisRefreshFlag=TRUE&filterByFeedback=ALL&fields=personIdentifier,reCiterArticleFeatures.pmid" -H "accept: application/json" -H "api-key: yourAPIkey" > ~/Desktop/reciterTest/paa2013.json
curl -X GET "https://reciter.weill.cornell.edu/reciter/feature-generator/by/uid?uid=tew2004&totalStandardizedArticleScore=1&useGoldStandard=AS_EVIDENCE&analysisRefreshFlag=TRUE&filterByFeedback=ALL&fields=personIdentifier,reCiterArticleFeatures.pmid" -H "accept: application/json" -H "api-key: yourAPIkey" > ~/Desktop/reciterTest/tew2004.json
curl -X GET "https://reciter.weill.cornell.edu/reciter/feature-generator/by/uid?uid=jobuck&totalStandardizedArticleScore=1&useGoldStandard=AS_EVIDENCE&analysisRefreshFlag=TRUE&filterByFeedback=ALL&fields=personIdentifier,reCiterArticleFeatures.pmid" -H "accept: application/json" -H "api-key: yourAPIkey" > ~/Desktop/reciterTest/jobuck.json
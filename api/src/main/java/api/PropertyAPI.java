package api;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.ItemCollection;
import com.amazonaws.services.dynamodbv2.document.Page;
import com.amazonaws.services.dynamodbv2.document.QueryOutcome;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.document.spec.QuerySpec;
import com.amazonaws.services.dynamodbv2.document.utils.ValueMap;

import java.util.Iterator;
import java.util.Map;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class PropertyAPI implements RequestHandler<Map<String, Object>, JSONObject> {
    public static void main(String[] args) {
        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_2)
                .build();
        DynamoDB dynamoDB = new DynamoDB(client);

        Table table = dynamoDB.getTable("redfin-listings-table");

        QuerySpec spec = new QuerySpec()
                .withKeyConditionExpression("zipcode = :zipcode")
                .withValueMap(new ValueMap()
                        .withString(":zipcode", "94133"));
                                        
        ItemCollection<QueryOutcome> items = table.query(spec);
        Iterator<Item> iterator = items.iterator();
        Item item = null;
        while (iterator.hasNext()) {
            item = iterator.next();
            JSONParser parser = new JSONParser();  
            try {
                JSONObject json = (JSONObject) parser.parse(item.getString("json_body"));
                System.out.println(json);
            } catch (ParseException e) {
                e.printStackTrace();
            }  
            break;
        }
    }

    @Override
    public JSONObject handleRequest(Map<String, Object> event, Context context) {
        LambdaLogger logger = context.getLogger();
        logger.log("EVENT: " + event.toString());

        JSONObject responseJson = new JSONObject();
        responseJson.put("statusCode", 200);
        responseJson.put("body", "Hello, world!");
        return responseJson;
    }
}
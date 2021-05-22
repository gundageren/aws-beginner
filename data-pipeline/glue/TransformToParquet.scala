import com.amazonaws.services.glue.GlueContext
import com.amazonaws.services.glue.util.GlueArgParser
import com.amazonaws.services.glue.util.Job
import org.apache.spark.SparkContext
import org.apache.spark.sql.SaveMode
import org.apache.spark.sql.SparkSession
import scala.collection.JavaConverters._

object TransformToParquet {
  def main(sysArgs: Array[String]) {
    val spark: SparkContext = new SparkContext()
    val glueContext: GlueContext = new GlueContext(spark)
    val sparkSession: SparkSession = glueContext.getSparkSession
    
    val args = GlueArgParser.getResolvedOptions(sysArgs, Seq("JOB_NAME", "table").toArray)
    Job.init(args("JOB_NAME"), glueContext, args.asJava)
    
    val table = args("table")
    
    val inputData = sparkSession.read
      .format("csv")
      .option("header", "true")
      .load(s"s3://<YourDatalakeBucket>/raw/$table/*.csv")
    
    val output = inputData.write
      .mode(SaveMode.Overwrite)
      .parquet(s"s3://<YourDatalakeBucket>/parquet/$table/")
    Job.commit()
  }
}
from source.helpers.connection import MongoConnection


class GetData:
    def __int__(self):
        ...

    @staticmethod
    def handle_sort(sort_type):
        return -1 if sort_type == "desc" else 1

    def executor(self, queries: dict, number_of_records: str = "15", page: str = "1", sort_name: str = "customerID",
                 sort_type: str = "asc", search_query=None):
        if search_query is None:
            search_query = {}
        sort_type = self.handle_sort(sort_type)
        with MongoConnection() as mongo:
            try:
                baskets = list(mongo.basket.find(
                    queries, {"_id": False, "basketJalaliCompleteTime": 0, "basketJalaliDeleteTime": 0}).limit(
                    int(number_of_records)).skip(
                    int(number_of_records) * (int(page) - 1)).sort(sort_name,
                                                                   sort_type))
                total_count = mongo.basket.count_documents(queries)
                data = {
                    "data": baskets,
                    "totalCount": total_count,
                }
                return {"success": True, "message": data, "status_code": 200}
            except Exception as e:
                return {"success": False, "error": e, "status_code": 404}

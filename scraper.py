import asyncio
import requests
import os
import inspect
from utils.parser import html_to_text

class Scraper:
    URL_PREF = "https://leetcode.com"
    def __init__(self):
        pass

    @staticmethod
    def _load_query(filename: str) -> str:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        queries_folder = os.path.join(script_dir, "gql_queries")
        file_path = os.path.join(queries_folder, filename)

        try:
            with open(file_path, 'r') as f:
                return f.read()
        
        except Exception as e:
            raise e

    @staticmethod
    async def _call_repeatedly(func, *args, max_retries: int = 3, delay: int = 2, **kwargs) -> any:
        for attempt in range(1, max_retries + 1):
            try:
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return await asyncio.to_thread(func, *args, **kwargs)

            except Exception as e:
                print(f"Attempt {attempt} failed with error: {e}")
                if attempt == max_retries:
                    print("Max retries reached. Giving up.")
                    raise

                sleep_time = delay * (2 ** (attempt - 1))
                print(f"Retrying in {sleep_time} seconds...")
                await asyncio.sleep(sleep_time)
        
        raise Exception("Max retries reached. Giving up")

    @staticmethod
    def _slugify(text: str) -> str:
        result = []
        last_was_sep = False
        for c in text:
            if c.isalpha():
                if last_was_sep and result:
                    result.append('-')
                result.append(c.lower())
                last_was_sep = False

            elif c.isdigit():
                if last_was_sep and result:
                    result.append('-')
                result.append(c)
                last_was_sep = False

            else:
                last_was_sep = True

        return "".join(result)

    def _post_query(self, query: dict) -> dict:
        api_url = self.URL_PREF + "/graphql/"
        print(f"Making POST request to {api_url}")
        try:
            response = requests.post(
                api_url,
                json = query,
                timeout = 10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise e

    async def scrape_daily_challenge(self) -> dict:
        try:
            problem_context_query = {
                "operationName": "questionOfTodayV2",
                "query": self._load_query("questionOfTodayV2.graphql"),
                "variables": {}
            }
        except Exception as e:
            raise e

        try:
            print("Fetching problem context...")
            response = await self._call_repeatedly(self._post_query, problem_context_query)
            print("Problem context fetched successfully.\n")

        except Exception as e:
            raise e

        problem_title_slug = response["data"]["activeDailyCodingChallengeQuestion"]["question"]["titleSlug"]
        problem_link = response["data"]["activeDailyCodingChallengeQuestion"]["link"]
        problem_id = response["data"]["activeDailyCodingChallengeQuestion"]["question"]["id"]
        problem_title = response["data"]["activeDailyCodingChallengeQuestion"]["question"]["title"]
        problem_full_title = problem_id + ". " + problem_title
        full_problem_link = self.URL_PREF + problem_link

        try:
            problem_details_data = {
                "operationName": "questionDetail",
                "query": self._load_query("questionDetail.graphql"),
                "variables": {
                    "titleSlug": problem_title_slug
                }
            }
        except Exception as e:
            raise e

        try:
            print("Fetching problem details...")
            response = await self._call_repeatedly(self._post_query, problem_details_data)
            print("Problem details fetched successfully.\n")

        except Exception as e:
            raise e

        problem_content = response["data"]["question"]["content"]

        try:
            solution_metadata_query = {
                "operationName": "ugcArticleSolutionArticles",
                "query": self._load_query("ugcArticleSolutionArticles.graphql"),
                "variables": {
                    "questionSlug": problem_title_slug,
                    "orderBy": "HOT",
                    "skip": 0,
                    "first": 15,
                    "tagSlugs": [],
                    "userInput": "",
                    "isMine": False
                }
            }
        except Exception as e:
            raise e

        try:
            print("Fetching solution metadata...")
            response = await self._call_repeatedly(self._post_query, solution_metadata_query)
            print("Solution metadata fetched successfully.\n")

        except Exception as e:
            raise e

        solutions = response["data"]["ugcArticleSolutionArticles"]["edges"]
        if len(solutions) <= 1:
            raise Exception("Failed to find community provided solution.")

        topic_id = solutions[1]["node"]["topicId"]
        try:
            solution_details_query = {
                "operationName": "ugcArticleSolutionArticle",
                "query": self._load_query("ugcArticleSolutionArticle.graphql"),
                "variables": {
                    "topicId": topic_id
                }
            }
        except Exception as e:
            raise e

        try:
            print("Fetching solution details...")
            response = await self._call_repeatedly(self._post_query, solution_details_query)
            print("Solution details fetched successfully.\n")

        except Exception as e:
            raise e

        solution_title = response["data"]["ugcArticleSolutionArticle"]["title"]
        solution_content = response["data"]["ugcArticleSolutionArticle"]["content"]
        full_solution_link = (
            self.URL_PREF +
            "/problems/" +
            problem_title_slug +
            "/solutions/" +
            str(topic_id) +
            "/" + self._slugify(solution_title)
        )
        
        parsed_problem_content = html_to_text(problem_content)
        return {
            "problem_link": full_problem_link,
            "problem_title": problem_full_title,
            "problem_desc": parsed_problem_content,
            "solution_link": full_solution_link,
            "solution_title": solution_title,
            "solution_desc": solution_content
        }

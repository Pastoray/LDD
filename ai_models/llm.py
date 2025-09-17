import ollama

class ContentGenerator:
    def __init__(self, model_name: str, max_content_len: int = 1800):
        self._model_name = model_name
        self._system_prompt = """
        You are a highly skilled and professional software engineer and technical writer. Your task is to provide a concise, analytical, and educational explanation of a programming problem and a common solution strategy.

        Your explanation must be written in a professional, objective tone. Do not use the first person ("I," "my," "we").

        Your response must strictly adhere to the following rules:
        1.  **Do not include any code snippets, code blocks, or pseudo-code whatsoever.** The explanation must be in plain, descriptive text.
        2.  The response should start with a brief, professional overview of the problem.
        3.  Then, it should describe a common logical approach or key insight to solve the problem. Use phrases like "A common approach involves..." or "The key insight to this problem is..."
        4.  After explaining the logic, briefly discuss the solution's implementation details and its time and space complexity.
        5.  The final sentence of your response must be a single, engaging question related to the problem and solution, designed to encourage reader discussion. Do not use a header or a label for this question.
        6.  Avoid all conversational filler, slang, and emojis. The tone should be similar to a professional academic paper or a high-quality technical blog.
        7.  Do not mention that a solution was provided to you.
        8.  **The entire response must not exceed 1,800 characters, including spaces.**
        """
        self._max_content_len = max_content_len
    
    def _create_user_prompt(
        self,
        problem_title: str,
        problem_desc: str,
        solution_title: str,
        solution_desc: str
    ) -> str:

        user_prompt = f"""
        Problem Title:
        {problem_title}
        
        Problem Description:
        {problem_desc}
        
        Solution Title:
        {solution_title}
        
        Solution Description:
        {solution_desc}
        """
        
        return user_prompt

    def generate_post(
        self,
        problem_title: str,
        problem_desc: str,
        solution_title: str,
        solution_desc: str,
        problem_link: str = None,
        solution_link: str = None
    ) -> str:
        ai_res = self._generate(
            problem_title,
            problem_desc,
            solution_title,
            solution_desc,
        )

        post_content = self._add_generic_content(
            ai_res,
            problem_title,
            problem_link,
            solution_link
        )
        return post_content

    def _generate(
        self,
        problem_title: str,
        problem_desc: str,
        solution_title: str,
        solution_desc: str,
    ) -> str:
        try:
            print("Sending data to Ollama for processing...")
            try:
                user_prompt = self._create_user_prompt(problem_title, problem_desc, solution_title, solution_desc)
                response = ollama.chat(
                    model = self._model_name,
                    messages = [
                        { "role": "system", "content": self._system_prompt },
                        { "role": "user", "content": user_prompt },
                    ]
                )

            except Exception as e:
                print(f"An error occurred while communicating with Ollama: {e}")
                raise

            ai_res = response["message"]["content"]
            if len(ai_res) > self._max_content_len:
                # Find the last sentence ending punctuation before the limit
                last_punc = max(
                    ai_res.rfind('.', 0, self._max_content_len),
                    ai_res.rfind('?', 0, self._max_content_len),
                    ai_res.rfind('!', 0, self._max_content_len)
                )

                if last_punc != -1:
                    truncated_res = ai_res[:last_punc + 1]

                else:
                    truncated_res = ai_res[:self._max_content_len] + "..."

                ai_res = truncated_res + "\n\nFor more details about this solution, don't hesitate to reach out; I'm always available!"
            
            return ai_res
        except:
            raise 

    def _add_generic_content(self, ai_res: str, problem_title: str, problem_link: str, solution_link: str) -> str:
        header = f"Today's Problem: {problem_title} 🚀\n"
        post_content = f"{header}{ai_res}\n\n"
        
        # links
        if problem_link is not None:
            post_content += f"Problem Link: {problem_link}\n"

        if solution_link is not None:
            post_content += f"Top Solution Link: {solution_link}\n"
            
        # generic set of hashtags
        post_content += "\n#coding #programming #softwareengineer #algorithms #leetcode #python"
        print("Generated post content successfully.")

        return post_content

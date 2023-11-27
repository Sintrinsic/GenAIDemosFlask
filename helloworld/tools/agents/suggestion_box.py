from chat.artificial_friend import ArtificialFriend


class SuggestionBox(ArtificialFriend):
    def __init__(self):
        model_name = 'gpt-4-1106-preview'
        agent_name = "assistant"
        identity_message = """
        You are a civil assistant working to interpret the needs of the public, and convert those needs into actionable suggestions for the government.
        You do so by reviewing a large set of comments, finding patterns in them, and creating a taxonomy of issues that 
        relates to the kind of work the local government can do, and the problems that exist. 
        
        Your reports should contain the following elements:
        A tree-like taxonomy of issue categories with a layer depth that matches the needs of the data. 
        Each node on the tree has a count of how many comments were found that match that category.
        You will then provide a summary section of any common complaints that seem to be arrising from the data.
        Lastly, your report will have a proposed action items section, prioritized by a cost to reward assessment. 
        
        """

        super().__init__(identity_message, model_name=model_name, agent_name=agent_name)

import gradio as gr
from utils import get_top_n_recommendations, get_next_unique_recommendations, get_random_desserts

last_recommendations = []
exclude_names = []

def start_selection(choice, budget, taste_filter, ingredient_exclude):
    global last_recommendations, exclude_names
    filters = ""
    if taste_filter != "none":
        filters += taste_filter + " "
    if ingredient_exclude != "none":
        filters += ingredient_exclude.replace("no ", "without ")

    if choice == "Dessert":
        last_recommendations = get_random_desserts(max_budget=budget)
    else:
        last_recommendations = get_top_n_recommendations(filters.strip(), budget)

    exclude_names = [r['name'] for r in last_recommendations]

    if not last_recommendations:
        return ["No suggestions found."] * 3

    suggestions = [f"{r['name']} ({r['price']} $)" for r in last_recommendations]
    while len(suggestions) < 3:
        suggestions.append("")

    return suggestions[:3]

def show_selected(index):
    if index is None or not last_recommendations:
        return "No selection made."
    
    index = int(index)
    if index >= len(last_recommendations):
        return "Selected suggestion is not available."

    selected = last_recommendations[index]

    # Eğer seçilen öneri boşsa (içerik yoksa), yine gösterme
    if not selected.get("name") or not selected.get("desc"):
        return "Selected suggestion is not available."

    return f"{selected['name']} ({selected['price']} TL)\n\nIngredients: {selected['desc']}"



def get_another_solution(choice, budget, taste_filter, ingredient_exclude):
    global last_recommendations, exclude_names
    filters = ""
    if taste_filter != "none":
        filters += taste_filter + " "
    if ingredient_exclude != "none":
        filters += ingredient_exclude.replace("no ", "without ")

    if choice == "Dessert":
        new_recommendations = get_random_desserts(max_budget=budget)
    else:
        new_recommendations = get_next_unique_recommendations(filters.strip(), budget, exclude_names)

    if not new_recommendations:
        return ["No more unique suggestions."] * 3

    last_recommendations = new_recommendations
    exclude_names.extend([r['name'] for r in new_recommendations])

    suggestions = [f"{r['name']} ({r['price']} $)" for r in new_recommendations]
    while len(suggestions) < 3:
        suggestions.append("")

    return suggestions[:3]


demo = gr.Blocks()

with demo:
    gr.Markdown(
        """
        # 🍽️ MealMatch AI – What would you like to eat?
        Choose whether you're in the mood for a dessert or a meal.
        Then select your preferences below.
        """
    )

    with gr.Row():
        with gr.Column():
            meal_type = gr.Dropdown(label="Choose Category", choices=["Dessert", "Meal"], value="Meal")
            taste_filter = gr.Dropdown(label="Taste Filter", choices=["none", "spicy", "sweet", "savory", "vegan"], value="none")
            ingredient_exclude = gr.Dropdown(label="Ingredient Exclusion", choices=["none", "no garlic", "no onion", "no cheese", "no egg", "no meat"], value="none")
            budget_input = gr.Number(label="Maximum Budget (in $)", value=50)
            suggest_btn = gr.Button("🍽️ Show Suggestions")
            another_btn = gr.Button("🔁 Get Another Solution")

        with gr.Column():
            suggestions_output = gr.Textbox(label="1st Suggestion")
            suggestions_output2 = gr.Textbox(label="2nd Suggestion")
            suggestions_output3 = gr.Textbox(label="3rd Suggestion")

    with gr.Row():
        select = gr.Radio(["0", "1", "2"], label="Which one do you like?")
        result_output = gr.Textbox(label="Your Selected Meal")
        select_btn = gr.Button("✅ Confirm Selection")

    suggest_btn.click(
        fn=start_selection,
        inputs=[meal_type, budget_input, taste_filter, ingredient_exclude],
        outputs=[suggestions_output, suggestions_output2, suggestions_output3]
    )

    another_btn.click(
        fn=get_another_solution,
        inputs=[meal_type, budget_input, taste_filter, ingredient_exclude],
        outputs=[suggestions_output, suggestions_output2, suggestions_output3]
    )

    select_btn.click(
        fn=show_selected,
        inputs=select,
        outputs=result_output
    )


demo.launch()
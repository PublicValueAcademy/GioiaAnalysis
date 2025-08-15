
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go
import json

import plotly.graph_objects as go
from typing import Tuple

from db.schema import settings



def load_json_in_DF()->Tuple:
    """load normalized data from json file"""
    filepath = settings.BASE_DIR / "03_files" / "normalized_second_level_themes.json"
    with open(filepath, "r") as json_file:
        raw_data = json.load(json_file)
    df = pd.json_normalize(raw_data[0]['themes'])
    df = df.rename(columns={"pattern_name": "Pattern Name",
            "weight":                       "Weight",
            "broader_aggregate_dimensions": "Dimensions",
            "reasoning":                    "Reasoning"})
    df_exploded = df.explode("Dimensions")
    df_sorted = df_exploded.sort_values(by=["Pattern Name", "Weight"])
    theme_weights =df_exploded.groupby("Pattern Name")["Weight"].sum().sort_values(ascending=False)

    return df,df_sorted, theme_weights





def weight_based_bar_chart(agg_weights:pd.DataFrame):
    """weight base bar chart"""
    filepath = settings.BASE_DIR / "04_Output" / "theme_weights_bar.png"
    plt.figure(figsize=(10, 6))
    agg_weights.plot(kind='bar', color='skyblue')
    plt.title(
        "Total Weights of Themes by Broader Aggregate Dimension")
    plt.ylabel("Sum of Theme Weights")
    plt.xlabel("Broader Aggregate Dimensions")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')

def sankey_bar_chart(df_exploded:pd.DataFrame):
    """sankey bar chart"""
    filepath = settings.BASE_DIR / "04_Output" / "theme_weights_sankey.png"
    nodes = list(df_exploded[
                     "Dimensions"].unique()) + list(
        df_exploded["Pattern Name"].unique())
    node_indices = {node: i for i, node in enumerate(nodes)}

    # Build source, target, value lists
    source = df_exploded[
        "Dimensions"].map(node_indices)
    target = df_exploded["Pattern Name"].map(node_indices)
    value = df_exploded["Weight"]

    # Create Sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes),
        link=dict(source=source, target=target,
            value=value)))

    fig.update_layout(
        title_text="Theme Weights by Aggregate Dimension (Sankey)",
        font_size=10)
    fig.write_image(filepath, scale=2)


def theme_heatmap(df_exploded: pd.DataFrame):
    """
    Creates a heatmap of theme weights by aggregate dimension.
    """
    # Create a pivot table: rows = Dimensions, columns = Pattern Name, values = Weight
    heatmap_data = df_exploded.pivot_table(
        index='Dimensions', columns='Pattern Name',
        values='Weight', aggfunc='sum', fill_value=0)

    # Plot the heatmap
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, annot=True, fmt="d",
                cmap="YlGnBu", cbar_kws={'label': 'Weight'})
    plt.title("Theme Weights by Aggregate Dimension")
    plt.xlabel("Theme")
    plt.ylabel("Aggregate Dimension")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the figure
    filepath = settings.BASE_DIR / "04_Output" / "theme_weights_heatmap.png"
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()

def theme_table(df_exploded: pd.DataFrame):
    """
    Creates an interactive table showing Themes, Aggregate Dimensions, Weights, and Reasoning.
    """
    # Prepare data columns
    table_data = [
        df_exploded["Pattern Name"],
        df_exploded["Dimensions"],
        df_exploded["Weight"],
        df_exploded["Reasoning"].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
    ]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Theme", "Aggregate Dimension", "Weight", "Reasoning"],
            fill_color='paleturquoise',
            align='left'
        ),
        cells=dict(
            values=table_data,
            fill_color='lavender',
            align='left'
        )
    )])

    # Save interactive HTML table
    filepath = settings.BASE_DIR / "04_Output" / "theme_table.html"
    fig.write_html(filepath)
    fig.show()


if __name__ == '__main__':
    data, data_exploded, data_weighted = load_json_in_DF()
    #weight_based_bar_chart(data_weighted)
    sankey_bar_chart(data_exploded)
    theme_heatmap(data_exploded)
    theme_table(data_exploded)
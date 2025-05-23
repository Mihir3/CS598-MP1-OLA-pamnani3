from HLL import HyperLogLog
from typing import List, Any

import pandas as pd
import plotly.graph_objects as go


class OLA:
    def __init__(self, widget: go.FigureWidget):
        """
            Base OLA class.

            *****************************************
            * You do not have to modify this class. *
            *****************************************

            @param widget: The dynamically updating plotly plot.
        """
        self.widget = widget

    def process_slice(df_slice: pd.DataFrame) -> None:
        """
            Process a dataframe slice. To be implemented in inherited classes.
        """
        pass

    def update_widget(self, groups_list: List[Any], values_list: List[Any]) -> None:
        """
            Update the plotly widget with newest groupings and values.

            @param groups_list: List of groups.
            @param values_list: List of grouped values (e.g., grouped means/sums).
        """
        self.widget.data[0]['x'] = groups_list
        self.widget.data[0]['y'] = values_list


class AvgOla(OLA):
    def __init__(self, widget: go.FigureWidget, mean_col: str):
        """
            Class for performing OLA by incrementally computing the estimated mean of *mean_col*.
            This class is implemented for you as an example.

            @param mean_col: column to compute filtered mean for.
        """
        super().__init__(widget)
        self.mean_col = mean_col

        # Bookkeeping variables
        self.sum = 0
        self.count = 0

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        """
            Update the running mean with a data frame slice.
        """
        self.sum += df_slice.sum()[self.mean_col]
        self.count += df_slice.count()[self.mean_col]

        # Update the plot. The mean should be put into a singleton list due to Plotly semantics.
        # Note: there is no x axis label since there is only one bar.
        self.update_widget([""], [self.sum / self.count])


class FilterAvgOla(OLA):
    def __init__(self, widget: go.FigureWidget, filter_col: str, filter_value: Any, mean_col: str):
        """
            Class for performing OLA by incrementally computing the estimated filtered mean of *mean_col*
            where *filter_col* is equal to *filter_value*.

            @param filter_col: column to filter on.
            @param filter_value: value to filter for, i.e., df[df[filter_col] == filter_value].
            @param mean_col: column to compute filtered mean for.
        """
        super().__init__(widget)
        self.filter_col = filter_col
        self.filter_value = filter_value
        self.mean_col = mean_col

        # Put any other bookkeeping class variables you need here...
        self.sum = 0
        self.count = 0


    def process_slice(self, df_slice: pd.DataFrame) -> None:
        """
            Update the running filtered mean with a dataframe slice.
        """
        # Implement me!
        df_slice = df_slice[df_slice[self.filter_col] == self.filter_value] 
        self.sum += df_slice.sum()[self.mean_col]
        self.count += df_slice.count()[self.mean_col]
       
        # Update the plot. The filtered mean should be put into a singleton list due to Plotly semantics.
        # hint: self.update_widget([""], *estimated filtered mean of mean_col*)
        self.update_widget([""], [self.sum / self.count])


class GroupByAvgOla(OLA):
    def __init__(self, widget: go.FigureWidget, groupby_col: str, mean_col: str):
        """
            Class for performing OLA by incrementally computing the estimated grouped means of *mean_col*
            with *groupby_col* as groups.

            @param groupby_col: grouping column, i.e., df.groupby(groupby_col).
            @param mean_col: column to compute grouped means for.
        """
        super().__init__(widget)
        self.groupby_col = groupby_col
        self.mean_col = mean_col

        # Put any other bookkeeping class variables you need here...
        self.group_sums = {}
        self.group_counts = {}

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        """
            Update the running grouped means with a dataframe slice.
        """
        # Implement me!
        grouped_df_slice = df_slice.groupby(self.groupby_col)
        for group_key, group_values in grouped_df_slice :
            group_sum = group_values[self.mean_col].sum()
            group_count = group_values[self.mean_col].count()

            if group_key in self.group_sums:
                self.group_sums[group_key] += group_sum
                self.group_counts[group_key] += group_count
            else:
                self.group_sums[group_key] = group_sum
                self.group_counts[group_key] = group_count

        # Update the plot
        # hint: self.update_widget(*list of groups*, *list of estimated group means of mean_col*)
        group_key_names = list(self.group_sums.keys())
        group_mean_values = [self.group_sums[group_key] / self.group_counts[group_key] if self.group_counts[group_key] != 0 else 0 for group_key in group_key_names]
        self.update_widget(group_key_names, group_mean_values) #check


class GroupBySumOla(OLA):
    def __init__(self, widget: go.FigureWidget, original_df_num_rows: int, groupby_col: str, sum_col: str):
        """
            Class for performing OLA by incrementally computing the estimated grouped sums of *sum_col*
            with *groupby_col* as groups.

            @param original_df_num_rows: number of rows in the original dataframe before sampling and slicing.
            @param groupby_col: grouping column, i.e., df.groupby(groupby_col).
            @param sum_col: column to compute grouped sums for.
        """
        super().__init__(widget)
        self.original_df_num_rows = original_df_num_rows
        self.groupby_col = groupby_col
        self.sum_col = sum_col

        # Put any other bookkeeping class variables you need here...
        self.group_sums = {}
        self.rows_seen = 0

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        """
            Update the running grouped sums with a dataframe slice.
        """
        # Implement me!
        self.rows_seen += len(df_slice)
        grouped_df_slice = df_slice.groupby(self.groupby_col)
    
        for group_key, group_values in grouped_df_slice :
            group_sum = group_values[self.sum_col].sum()

            if group_key in self.group_sums:
                self.group_sums[group_key] += group_sum
            else:
                self.group_sums[group_key] = group_sum
        # Update the plot
        # hint: self.update_widget(*list of groups*, *list of estimated grouped sums of sum_col*)
        group_key_names = list(self.group_sums.keys())
        group_sum_values= list(self.group_sums.values())
        scaled_group_sum_values = [value * (self.original_df_num_rows / self.rows_seen) for value in group_sum_values]
        self.update_widget(group_key_names, scaled_group_sum_values)  


class GroupByCountOla(OLA):
    def __init__(self, widget: go.FigureWidget, original_df_num_rows: int, groupby_col: str, count_col: str):
        """
            Class for performing OLA by incrementally computing the estimated grouped non-null counts in *count_col*
            with *groupby_col* as groups.

            @param original_df_num_rows: number of rows in the original dataframe before sampling and slicing.
            @param groupby_col: grouping column, i.e., df.groupby(groupby_col).
            @param count_col: counting column.
        """
        super().__init__(widget)
        self.original_df_num_rows = original_df_num_rows
        self.groupby_col = groupby_col
        self.count_col = count_col

        # Put any other bookkeeping class variables you need here...
        self.group_counts = {}
        self.rows_seen = 0

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        """
            Update the running grouped counts with a dataframe slice.
        """
        # Implement me!
        self.rows_seen += len(df_slice)
        grouped_df_slice = df_slice.groupby(self.groupby_col)

        for group_key, group_values in grouped_df_slice :
            group_count = group_values[self.count_col].count()

            if group_key in self.group_counts:
                self.group_counts[group_key] += group_count
            else:
                self.group_counts[group_key] = group_count

        for group_key in self.group_counts:
            group_count = self.group_counts[group_key]

        # Update the plot
        # hint: self.update_widget(*list of groups*, *list of estimated group counts of count_col*)
        group_key_names = list(self.group_counts.keys())
        group_count_values = list(self.group_counts.values())
        scaled_group_count_values = [value * (self.original_df_num_rows / self.rows_seen) for value in group_count_values]
        self.update_widget(group_key_names, scaled_group_count_values)  


class FilterDistinctOla(OLA):
    def __init__(self, widget: go.FigureWidget, filter_col: str, filter_value: Any, distinct_col: str):
        """
            Class for performing OLA by incrementally computing the estimated cardinality (distinct elements) *distinct_col*
            where *filter_col* is equal to *filter_value*.

            @param filter_col: column to filter on.
            @param filter_value: value to filter for, i.e., df[df[filter_col] == filter_value].
            @param distinct_col: column to compute cardinality for.
        """
        super().__init__(widget)
        self.filter_col = filter_col
        self.filter_value = filter_value
        self.distinct_col = distinct_col

        # HLL for estimating cardinality. Don't modify the parameters; the autograder relies on it.
        # IMPORTANT: Please convert your data to the String type before adding to the HLL, i.e., self.hll.add(str(data))
        self.hll = HyperLogLog(p=2, seed=123456789)

        # Put any other bookkeeping class variables you need here...

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        """
            Update the running filtered cardinality with a dataframe slice.
        """
        # Implement me!
        df_slice = df_slice[df_slice[self.filter_col] == self.filter_value]
        distinct_values = df_slice[self.distinct_col].astype(str).tolist()
        distinct_estimates = []
        for value in distinct_values:
            self.hll.add(str(value))
            distinct_estimate = self.hll.cardinality()
        distinct_estimates.append(distinct_estimate)

        # Update the plot. The filtered cardinality should be put into a singleton list due to Plotly semantics.
        # hint: self.update_widget([""], *estimated filtered cardinality of distinct_col*)
        self.update_widget([""], [distinct_estimates])

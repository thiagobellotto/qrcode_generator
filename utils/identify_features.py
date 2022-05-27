from collections import Counter
from quantulum3.parser import parse
from scipy import stats
import re
import numpy as np
import pandas as pd


class identify_features:
    def __init__(self, df):
        self.df = df
        self._identify_types()

    def identify_process(self):
        """
        This function takes a dataframe and returns a dictionary of the data types of each column
        :return: The type of each feature in the dataframe.
        """
        self.type = {}
        for i in self.df:
            self.type[i] = self.identify_type_feature(self.df[i])

        self.type = self.get_list_of_values_from_dict(self.type)

        return self.type

    def get_list_of_values_from_dict(self, dict_types):
        """
        This function returns a list of values from a dictionary.
        :return: List of values from a dictionary.
        """
        values = []
        for i in dict_types:
            values.append(dict_types[i])
        return values

    def identify_type_feature(self, X, card_alta: float = 0.6, class_number: int = 8):
        """
        It identifies the type of feature based on the cardinality of the feature, the type of the
        feature, the number of unique values, and the number of classes.

        :param X: The column you want to identify the type of
        :param card_alta: float = 0.6
        :param class_number: The number of classes that you want to consider as a "many classes" variable, defaults to 8

        :return: the type of the feature.
        """

        # Cardinalidade dos dados
        cardinalidade = len(X.unique()) / len(X)
        num_val_unique = len(X.unique())

        # Identificando o tipo do dado
        tipo_coluna = self._columns_and_types[X.name]

        # Valores que são para marcação de null
        list_of_list = list(
            map(
                lambda x: [
                    ((-1) * (10**x)) + 1,
                    (-1) * (10**x),
                    ((-1) * (10**x)) - 1,
                ],
                range(1, 13),
            )
        )
        val_null = [item for sublist in list_of_list for item in sublist]

        # Try para pegar a unidade
        def try_parse(element):
            try:
                return parse(element)[0].unit.name
            except Exception as e:
                return "None"

        if cardinalidade >= card_alta:
            if cardinalidade == 1.0:
                if tipo_coluna == "string" or "object":
                    return "ID"
                elif tipo_coluna == "int" or "int32":
                    return "index"
                elif tipo_coluna == "float":
                    return "float"
            else:
                group_by = False
                if group_by is True:
                    pass
                else:
                    if tipo_coluna == "int" or tipo_coluna == "int32":
                        # Verificando se tem algum desses valores dentro da coluna
                        intersection = len(set(val_null).intersection(set(X))) > 0
                        # Tentando ver se todos os valores são positivos
                        positive = all(X > 0)
                        if intersection is True and positive is True:
                            return "integer"
                        else:
                            # Tentando obter o p-valor para negar a distribuição uniforme
                            p_valor = stats.kstest(
                                X, stats.uniform(loc=0.0, scale=max(X)).cdf
                            ).pvalue
                            accept_uniform = 0.5
                            if p_valor > accept_uniform:
                                return "index"
                            else:
                                return "integer"
                    elif tipo_coluna == "float":
                        return "float"
                    elif tipo_coluna == "string" or tipo_coluna == "object":

                        # Vendo se a maioria dos valores tem numeros
                        number_in_majority = (
                            X.apply(
                                lambda x: len(re.findall("[0-9]+", str(x))) > 0
                            ).sum()
                            / len(X)
                            > 0.5
                        )
                        if number_in_majority is True:

                            X = X.apply(lambda x: re.sub("\s\s+", " ", str(x)))
                            units = X.apply(lambda x: try_parse(str(x)))
                            have_units = (
                                stats.mode(units, axis=0, nan_policy="omit").mode[0]
                                == "None"
                            )

                            if have_units is True:
                                return stats.mode(
                                    units, axis=0, nan_policy="omit"
                                ).mode[0]
                            else:
                                media_str = np.mean(
                                    X.dropna().apply(lambda x: len(str(x)))
                                )

                                if media_str <= 50:
                                    if len(X.unique()) > 50:
                                        return "text"
                                    else:
                                        return "many classes"
                                else:
                                    return "text"

                        else:
                            media_str = np.mean(X.dropna().apply(lambda x: len(str(x))))

                            if media_str <= 50:
                                if len(X.unique()) > 50:
                                    return "text"
                                else:
                                    return "many classes"

                            else:
                                return "text"

                    # Returning the type of the feature as date.
                    elif tipo_coluna == "date":
                        return "date"

        else:
            # This is the part of the code that identifies the type of feature based on the cardinality of the
            # feature, the type of the feature, the number of unique values, and the number of classes.
            if num_val_unique <= class_number:

                if num_val_unique == 1:
                    return "constant"
                elif num_val_unique == 2:
                    return "bool"

                elif num_val_unique >= 3:
                    return "class"

            else:
                if tipo_coluna == "float":
                    return "float"

                elif tipo_coluna == "int" or tipo_coluna == "int32":
                    return "integer"

                elif tipo_coluna == "string" or tipo_coluna == "object":

                    # Vendo se a maioria dos valores tem numeros
                    number_in_majority = (
                        X.apply(lambda x: len(re.findall("[0-9]+", str(x))) > 0).sum()
                        / len(X)
                        > 0.5
                    )
                    if number_in_majority is True:

                        X = X.apply(lambda x: re.sub("\s\s+", " ", str(x)))
                        units = X.apply(lambda x: try_parse(str(x)))
                        have_units = (
                            stats.mode(units, axis=0, nan_policy="omit").mode[0]
                            == "None"
                        )

                        if have_units is True:

                            return stats.mode(units, axis=0, nan_policy="omit").mode[0]

                        else:

                            media_str = np.mean(X.dropna().apply(lambda x: len(str(x))))

                            if media_str <= 50:
                                if len(X.unique()) > 50:
                                    return "text"
                                else:
                                    return "many classes"

                            else:
                                return "text"

                    else:

                        media_str = np.mean(X.dropna().apply(lambda x: len(str(x))))
                        if media_str <= 50:
                            if len(X.unique()) > 50:
                                return "text"
                            else:
                                return "many classes"

                        else:
                            return "text"

                elif tipo_coluna == "date":
                    return "date"

    def _identify_types(self):
        """
        Identify types of columns and return in dict with type and list with name columns.
        Parameters
        -----------
        X: DataFrame with columns
        index: IF == False return name columns IF==True return index number
        """

        ## Converts the column types to the most suitable ones
        types = self.df.convert_dtypes().dtypes

        ## Create lists to obtain the datatypes with columns name
        string_list = list(types[types == pd.StringDtype()].index)
        object_list = list(types[types == object].index)
        boolean_list = list(types[types == pd.BooleanDtype()].index)
        float_list = list(types[types == pd.Float64Dtype()].index)
        int_list = list(types[types == pd.Int64Dtype()].index)
        int32_list = list(types[types == pd.Int32Dtype()].index)
        date_list = list(types[types == np.dtype("<M8[ns]")].index)

        number_of_columns = len(
            string_list
            + object_list
            + boolean_list
            + float_list
            + int_list
            + int32_list
            + date_list
        )

        ## Check for errors in the dataframe
        if number_of_columns != len(self.df.columns):
            raise Exception(
                f"Error has non-class column type. Colums in dataframe: {number_of_columns}. Number of columns: {len(self.df.columns)}"
            )

        columns_types_name = {
            "string": string_list,
            "object": object_list,
            "boolean": boolean_list,
            "float": float_list,
            "int": int_list,
            "int32": int32_list,
            "date": date_list,
        }

        self._types_and_columns_name = columns_types_name

        ## return index number of the columns
        string_list = [self.df.columns.get_loc(c) for c in string_list if c in self.df]
        object_list = [self.df.columns.get_loc(c) for c in object_list if c in self.df]
        boolean_list = [
            self.df.columns.get_loc(c) for c in boolean_list if c in self.df
        ]
        float_list = [self.df.columns.get_loc(c) for c in float_list if c in self.df]
        int_list = [self.df.columns.get_loc(c) for c in int_list if c in self.df]
        int32_list = [self.df.columns.get_loc(c) for c in int32_list if c in self.df]
        date_list = [self.df.columns.get_loc(c) for c in date_list if c in self.df]

        ## Save results in dictionary
        columns_types_index = {
            "string": string_list,
            "object": object_list,
            "boolean": boolean_list,
            "float": float_list,
            "int": int_list,
            "int32": int32_list,
            "date": date_list,
        }

        self._types_and_columns_index = columns_types_index

        type_columns = {}
        for j in columns_types_name:
            if columns_types_name[j] != []:
                for k in columns_types_name[j]:
                    type_columns[k] = j

        self._columns_and_types = type_columns

"""Compute the F1 score."""
from psycopg import sql

from zeno_backend.classes.base import GroupMetric
from zeno_backend.database.database import Database
from zeno_backend.database.select import column_id_from_name_and_model


def recall(project: str, model: str, filter: sql.Composed | None) -> GroupMetric:
    """Ratio of tp/(tp+fn), intuitively the ability to find all the positive samples.

    We use "macro" averaging, which means that we calculate the metric for each label
    and then take the unweighted mean, not accounting for class imbalance.

    Args:
        project (str): the project the user is currently working with.
        model (str): the model from which to take the predictions.
        filter (sql.Composed | None): filter applied before calculating the metic.

    Returns:
        GroupMetric: recall score for the group of filtered instances as specified.
    """
    output_column_id = column_id_from_name_and_model(project, "output", model)
    with Database() as db:
        tp_query = sql.SQL("SELECT COUNT(*), label FROM {} WHERE {} = label").format(
            sql.Identifier(project), sql.Identifier(output_column_id)
        )
        group_query = sql.SQL(" GROUP BY label;")
        num_tp = db.execute_return(
            tp_query + group_query
            if filter is None
            else tp_query + sql.SQL(" AND ") + filter + group_query
        )
        fn_query = sql.SQL("SELECT COUNT(*), label FROM {} WHERE {} != label").format(
            sql.Identifier(project), sql.Identifier(output_column_id)
        )
        num_fn = db.execute_return(
            fn_query + group_query
            if filter is None
            else fn_query + sql.SQL(" AND ") + filter + group_query
        )
        total_query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(project))
        num_total = db.execute_return(
            total_query
            if filter is None
            else total_query + sql.SQL(" WHERE ") + filter,
        )
        labels_query = sql.SQL("SELECT DISTINCT label FROM {}").format(
            sql.Identifier(project)
        )
        label_result = db.execute_return(
            labels_query
            if filter is None
            else labels_query + sql.SQL(" WHERE ") + filter
        )
        if (
            num_tp is None
            or num_fn is None
            or num_total is None
            or label_result is None
            or not isinstance(num_total[0], int)
        ):
            return GroupMetric(metric=None, size=0)
        metrics: list[float] = []
        tp_map: dict[str, int] = {}
        fn_map: dict[str, int] = {}
        labels: list[str] = []
        for label in label_result:
            if isinstance(label[0], str):
                labels.append(label[0])
        for label in labels:
            tp_map[label] = 0
            fn_map[label] = 0
        for item in num_tp:
            tp_map[item[1]] = item[0]
        for item in num_fn:
            fn_map[item[1]] = item[0]
        for label in labels:
            tp = tp_map[label]
            fn = fn_map[label]
            if tp + fn == 0:
                metrics.append(0)
            else:
                metrics.append(tp / (tp + fn))
        return GroupMetric(
            metric=100 * sum(metrics) / len(metrics) if len(metrics) > 0 else 0,
            size=num_total[0],
        )


def precision(project: str, model: str, filter: sql.Composed | None) -> GroupMetric:
    """Ratio of tp/(tp+fn), intuitively the ability to find all the positive samples.

    We use "macro" averaging, which means that we calculate the metric for each label
    and then take the unweighted mean, not accounting for class imbalance.

    Args:
        project (str): the project the user is currently working with.
        model (str): the model from which to take the predictions.
        filter (sql.Composed | None): filter applied before calculating the metic.

    Returns:
        GroupMetric: recall score for the group of filtered instances as specified.
    """
    output_column_id = column_id_from_name_and_model(project, "output", model)
    with Database() as db:
        tp_query = sql.SQL("SELECT COUNT(*), label FROM {} WHERE {} = label").format(
            sql.Identifier(project), sql.Identifier(output_column_id)
        )
        group_query = sql.SQL(" GROUP BY label;")
        num_tp = db.execute_return(
            tp_query + group_query
            if filter is None
            else tp_query + sql.SQL(" AND ") + filter + group_query
        )
        fp_query = sql.SQL("SELECT COUNT(*), {} FROM {} WHERE {} != label").format(
            sql.Identifier(output_column_id),
            sql.Identifier(project),
            sql.Identifier(output_column_id),
        )
        group_query = sql.SQL(" GROUP BY {};").format(sql.Identifier(output_column_id))
        num_fp = db.execute_return(
            fp_query + group_query
            if filter is None
            else fp_query + sql.SQL(" AND ") + filter + group_query
        )
        total_query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(project))
        num_total = db.execute_return(
            total_query
            if filter is None
            else total_query + sql.SQL(" WHERE ") + filter,
        )
        labels_query = sql.SQL("SELECT DISTINCT label FROM {}").format(
            sql.Identifier(project)
        )
        label_result = db.execute_return(
            labels_query
            if filter is None
            else labels_query + sql.SQL(" WHERE ") + filter
        )
        if (
            num_tp is None
            or num_fp is None
            or num_total is None
            or label_result is None
            or not isinstance(num_total[0], int)
        ):
            return GroupMetric(metric=None, size=0)
        metrics: list[float] = []
        tp_map: dict[str, int] = {}
        fp_map: dict[str, int] = {}
        labels: list[str] = []
        for label in label_result:
            if isinstance(label[0], str):
                labels.append(label[0])
        for label in labels:
            tp_map[label] = 0
            fp_map[label] = 0
        for item in num_tp:
            tp_map[item[1]] = item[0]
        for item in num_fp:
            fp_map[item[1]] = item[0]
        for label in labels:
            tp = tp_map[label]
            fp = fp_map[label]
            if tp + fp == 0:
                metrics.append(0)
            else:
                metrics.append(tp / (tp + fp))
        return GroupMetric(
            metric=100 * sum(metrics) / len(metrics) if len(metrics) > 0 else 0,
            size=num_total[0],
        )


def f1(project: str, model: str, filter: sql.Composed | None) -> GroupMetric:
    """Compute the F1 score.

    We use "macro" averaging, which means that we calculate the metric for each label
    and then take the unweighted mean, not accounting for class imbalance.

    Args:
        project (str): the project the user is currently working with.
        model (str): the model from which to take the predictions.
        filter (sql.Composed | None): filter applied before calculating the metic.

    Returns:
        GroupMetric: f1 score for the group of filtered instances as specified.
    """
    prec = precision(project, model, filter)
    rec = recall(project, model, filter)
    if (
        prec.metric is None
        or rec.metric is None
        or prec.metric == 0
        and rec.metric == 0
    ):
        return GroupMetric(metric=None, size=prec.size)
    else:
        return GroupMetric(
            metric=2 * (prec.metric * rec.metric) / (prec.metric + rec.metric),
            size=prec.size,
        )
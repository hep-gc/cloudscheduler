if 'Table' not in locals() and 'Table' not in globals():
  from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey
  metadata = MetaData()


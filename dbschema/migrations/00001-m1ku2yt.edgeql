CREATE MIGRATION m1ku2ytyowfol7fn7ts5guox2vr5txq6tkssa575qxw5zgfwchfeha
    ONTO initial
{
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::Kek {
      CREATE PROPERTY pek: std::str;
  };
};
